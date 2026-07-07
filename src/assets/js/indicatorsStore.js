const initIndicatorsStore = () => {
    Alpine.store('indicators', {
        indicators: {},
        indicatorResults: [],
        indicatorsData: [],
        indicatorDataIndexById: {},
        indicatorDataIndexByCode: {},
        indicatorIdByCode: {},
        indicatorsSets: [],
        fieldTypes: {
            STRING: "S",
            TEXT: "T",
            INTEGER: "I",
            DECIMAL: "DC",
            BOOLEAN: "B",
            DATE: "D",
            ATTACHMENT: "A",
            CHECKBOX: "CH",
            RADIOBUTTON: "R",
            DROPDOWN: "DR",
            INTEGERGENDER: "IG",
            DECIMALGENDER: "DG",
        },
        initIndicators(indicators) {
            this.indicatorsData = indicators

            let indicatorsInSets = []
            this.indicatorsSets.forEach(s => indicatorsInSets = [...indicatorsInSets, ...s.indicators_ids])
            indicators.forEach(i => {
                // If indicator belongs to set
                if (indicatorsInSets.findIndex(iIS => iIS == i.id) != -1) {
                    // Find all instances
                    let instancesIds = Object.keys(indicatorResults).filter(instanceId => instanceId.includes(i.id))
                    if (instancesIds.length != 0) {
                        instancesIds.forEach(instanceId => this.indicators[instanceId] = {
                            value: '',
                            show: false,
                            notApplicable: false,
                            isValid: false,
                            isFieldValid: false,
                            hasErrors: false,
                            error: '',
                        })
                    } else {
                        // Or else, if no set indicator results have been saved yet, create empty entry for instance 1
                        this.indicators[`${i.id}_1`] = {
                            value: '',
                            show: false,
                            notApplicable: false,
                            isValid: false,
                            isFieldValid: false,
                            hasErrors: false,
                            error: '',
                        }
                    }
                } else {
                    this.indicators[i.id] = {
                        value: '',
                        show: false,
                        notApplicable: false,
                        isValid: false,
                        isFieldValid: false,
                        hasErrors: false,
                        error: '',
                    }
                }
            })

            this.storeMaps()

            const initEvent = new Event('indicators-store:init')
            document.dispatchEvent(initEvent)
        },
        parseExpression(expr, instanceId, val) {
            const tokens = expr.split(" ")

            // If expression is only a reference to another indicator return '__copy__' to copy its value
            if (tokens.length == 1 && this.indicatorDataIndexById[tokens[0]]) {
                return '__copy__'
            }

            let loadedTokens = []
            for (let token of tokens) {
                let value = null
                if (token.match(/^[a-zA-Z]\w*/)) {
                    if (token.match(/(_)/)) {
                        // Reference to other group indicator
                        const subtokens = token.split("_")
                        if (subtokens.includes('total')) {
                            // Load gendered field, list or table column total
                            value = this.loadTotalIndicatorResult(this.getInstanceId(subtokens[0], instanceId), subtokens)
                        } else if (subtokens.includes('set')) {
                            // Add set instances total
                            value = this.loadSetIndicatorTotal(subtokens[0])
                        } else {
                            value = subtokens.length == 2 ? this.loadIndicatorResult(this.getInstanceId(subtokens[0], instanceId), subtokens[1]) : this.loadIndicatorResult(this.getInstanceId(subtokens[0], instanceId), subtokens[1], subtokens[2])
                        }
                    } else if (token == 'val' && val.match(/(_)/)) {
                        // Reference to current group indicator
                        const subtokens = val.split("_")
                        value = subtokens.length == 2 ? this.loadIndicatorResult(instanceId, subtokens[1]) : this.loadIndicatorResult(instanceId, subtokens[1], subtokens[2])
                    } else if (token == 'val') {
                        // Reference to current indicator 
                        value = this.loadIndicatorResult(instanceId)
                    } else if (token == 'AND' || token == 'and') {
                        value = '&&'
                    } else if (token == 'OR' || token == 'or') {
                        value = '||'
                    } else if (token == 'true' || token == 'false' || token == 'null') {
                        value = token
                    } else {
                        // Reference to other indicator
                        if (this.belongsToSet(token)) {
                            value = this.loadIndicatorResult(this.getInstanceId(token, instanceId))
                        } else {
                            value = this.loadIndicatorResult(this.getInstanceId(token))
                        }
                    }
                    if (value == undefined) {
                        this.indicators[instanceId].hasErrors = true
                        this.indicators[instanceId].error = `Missing value, please fill question ${token} before.`
                        console.log(`Missing value, please fill question ${token} before.`)
                        return "false"
                    }
                    loadedTokens.push(value)
                } else if (token == "=") {
                    token = "=="
                    loadedTokens.push(token)
                } else {
                    loadedTokens.push(token)
                }
            }
            const jsExpr = loadedTokens.join(" ")

            return jsExpr
        },
        evaluateExpression(expr, instanceId, val = '') {
            try {
                const parsedExpression = this.parseExpression(expr, instanceId, val)
                if (parsedExpression == '__copy__') {
                    return '__copy__'
                }
                return eval(parsedExpression)
            } catch (e) {
                throw e
            }
        },
        validateField(instanceId, suffix = '', suffix2 = '', validateGroupItem = false, setGroupItems = false) {

            const id = instanceId.split('_')[0]
            const indicator = this.getIndicatorDataById(id)
            const code = indicator.code

            let result = {
                isValid: true,
                isFieldValid: true
            }

            let fieldEl = null
            let fieldData = null
            // If errors have to be display in a table, get the element for later manipulation
            if (setGroupItems) {
                fieldEl = document.querySelector(`#field_${instanceId}`)
                fieldData = Alpine.$data(fieldEl)
            }

            if (this.indicators[instanceId].notApplicable) {
                return result
            }

            // Simple fields without validation expression are true when a value is assigned
            if (
                (indicator.validation == '' && this.indicators[instanceId].value !== null && this.indicators[instanceId].value !== "" && !(this.indicators[instanceId].value instanceof Object)) ||
                (indicator.validation == '' && this.indicators[instanceId].value instanceof Object && !indicator.is_group_indicator && (this.indicators[instanceId].value.value !== null || this.indicators[instanceId].value.female !== undefined)) ||
                (indicator.validation == '' && this.indicators[instanceId].value instanceof Array && !indicator.is_group_indicator && this.indicators[instanceId].value.length > 0)
            ) {
                return result
            }

            // Empty non mandatory fields
            if (
                !indicator.mandatory && // Non mandatory
                (this.indicators[instanceId].value == null || this.indicators[instanceId].value == "" || // Empty string or number
                    (this.indicators[instanceId].value instanceof Object && !indicator.is_group_indicator &&  // Object value butno group indicator
                        (this.indicators[instanceId].value.value == null || this.indicators[instanceId].value.female == null) // Dropdown/checkbock or gendered field
                    )
                )
            ) {
                return result
            }

            try {
                if (indicator.is_group_indicator && !Array.isArray(this.indicators[instanceId].value) && this.indicators[instanceId].value !== null) {
                    // Validate lists and tables
                    result.isValid = this.indicators[instanceId].isValid instanceof Object ? this.indicators[instanceId].isValid : {}

                    if (indicator.group_2_items) {
                        indicator.group_items.forEach(({ suffix: k }) => {
                            if (result.isValid[k] == undefined) {
                                result.isValid[k] = {}
                            }
                            indicator.group_2_items.forEach(({ suffix: k2 }) => {
                                // Only validate for the current groupItem or if the whole field has to be validated
                                if (!validateGroupItem || (validateGroupItem && `${code}_${k}_${k2}` == `${code}_${suffix}_${suffix2}`)) {
                                    if (!indicator.mandatory && (this.indicators[instanceId].value[k][k2] === null || this.indicators[instanceId].value[k][k2] === '')) {
                                        // Empty non mandatory is valid
                                        result.isValid[k][k2] = true
                                    } else if (indicator.mandatory && (this.indicators[instanceId].value[k][k2] === null || this.indicators[instanceId].value[k][k2] === '')) {
                                        // Empty mandatory is not valid
                                        result.isValid[k][k2] = false
                                    } else {
                                        result.isValid[k][k2] = indicator.validation == '' ? true : !!this.evaluateExpression(indicator.validation, instanceId, `${code}_${k}_${k2}`)
                                    }
                                }
                                if (!result.isValid[k][k2]) {
                                    result.isFieldValid = false
                                }
                                if (setGroupItems) {
                                    fieldData.setGroupItemValid(k, k2)
                                }
                            })
                        })
                    } else {
                        indicator.group_items.forEach(({ suffix: k }) => {
                            // Only validate for the current groupItem or if the whole field has to be validated
                            if (!validateGroupItem || (validateGroupItem && `${code}_${k}` == `${code}_${suffix}`)) {
                                if (!indicator.mandatory && (this.indicators[instanceId].value[k] === null || this.indicators[instanceId].value[k] === '')) {
                                    // Empty non mandatory is valid
                                    result.isValid[k] = true
                                } else if (indicator.mandatory && (this.indicators[instanceId].value[k] === null || this.indicators[instanceId].value[k] === '')) {
                                    // Empty mandatory is not valid
                                    result.isValid[k] = false
                                } else {
                                    result.isValid[k] = indicator.validation == '' ? true : !!this.evaluateExpression(indicator.validation, instanceId, `${code}_${k}`)
                                }
                            }
                            if (!result.isValid[k]) {
                                result.isFieldValid = false
                            }
                            if (setGroupItems) {
                                fieldData.setGroupItemValid(k)
                            }
                        })
                    }
                } else {
                    // Validate simple indicators
                    result.isValid = !!this.evaluateExpression(indicator.validation, instanceId, code)
                    result.isFieldValid = result.isValid
                }
                return result
            } catch (e) {
                console.log("error in validation", e, indicator)

                return {
                    isValid: false,
                    isFieldValid: false
                }
            }
        },
        isVisible(instanceId, condition) {
            try {
                return this.evaluateExpression(condition, instanceId)
            } catch (e) {
                return false
            }
        },
        loadIndicatorResult(instanceId, suffix = "", suffix2 = "") {
            const instanceIdTokens = instanceId.split('_')
            const id = instanceIdTokens[0]
            const indicator = this.getIndicatorDataById(id)

            let result = null

            if (this.hasOptions(indicator.data_type)) {
                if (this.isMultiAnswer(indicator.data_type)) {
                    result = this.indicators[instanceId].value.reduce((prev, curr) => prev + curr.value, 0)
                } else {
                    result = this.indicators[instanceId].value.value
                }
            } else if (indicator.data_type == this.fieldTypes.BOOLEAN) {
                result = this.indicators[instanceId].value == 'True' ? 'true' : 'false'
            } else if (indicator.data_type == this.fieldTypes.STRING) {
                result = `'${this.indicators[instanceId].value}'`
            } else if (suffix != "") {
                if (suffix2 == "") {
                    result = Number(this.indicators[instanceId].value[suffix])
                } else {
                    result = this.indicators[instanceId].value[suffix][suffix2]
                }

            } else {
                result = this.indicators[instanceId].value || null
            }

            if (indicator.mandatory) {
                const notApplicableElem = document.getElementById(`question_${indicator.id}_na`)
                if (notApplicableElem && notApplicableElem.checked)
                    result = 0
            }

            if (result === null || (indicator.data_type != this.fieldTypes.STRING && result === "")) {
                result = 'null'
            }

            return result
        },
        loadTotalIndicatorResult(instanceId, subtokens) {
            let result = null
            if (subtokens.length == 2) {
                // List or table total
                result = this.indicators[instanceId].value.total
            } else if (subtokens.length == 3) {
                // Table row or column total
                result = this.indicators[instanceId].value[subtokens[1]].total
            } else {
                console.log("Invalid total token ")
                result = 0
            }
            if (result === null) {
                result = 'null'
            }
            return result
        },
        loadSetIndicatorTotal(code) {
            const indicator = this.getIndicatorDataByCode(code)
            const instancesKeys = Object.keys(this.indicators).filter(k => k.includes(indicator.id))
            return instancesKeys.reduce((acc, k) => acc + Number(this.indicators[k].value), 0)
        },
        updateIndicatorDependencies(instanceId) {
            const instanceIdTokens = instanceId.split('_')
            const id = instanceIdTokens[0]
            const instanceNumber = instanceIdTokens.length == 2 ? instanceIdTokens[1] : -1
            const indicator = this.getIndicatorDataById(id)
            if (indicator && indicator.dependant_indicators) {
                for (dependantIndicatorCode of indicator.dependant_indicators) {
                    this.updateDependantIndicator(instanceNumber, dependantIndicatorCode, indicator.code)
                }
            }
        },
        updateDependantIndicator(instanceNumber, dependantIndicatorCode, code) {
            const indicator = this.getIndicatorDataByCode(dependantIndicatorCode)
            let updated = false
            if (indicator) {
                let instanceId = instanceNumber == -1 ? indicator.id : `${indicator.id}_${instanceNumber}`

                // Check which expressions are dependent of this indicator
                // Check if condition is dependant
                if (indicator.condition.includes(code)) {
                    let fieldEl = document.querySelector(`#field_${instanceId}`);
                    // If no element found check set instance
                    if (fieldEl == null) {
                        instanceId = instanceId + "_1"
                        fieldEl = document.querySelector(`#field_${instanceId}`);
                    }
                    const show = this.isVisible(instanceId, indicator.condition)
                    Alpine.$data(fieldEl).updateShow(show)

                    // Set NA of direct indicator 
                    if (indicator.is_direct_indicator && !show) {
                        Alpine.$data(fieldEl).updateNotApplicable(true, true)
                    }

                    // Update validation
                    const { isValid, isFieldValid } = this.validateField(instanceId)
                    this.indicators[instanceId].isValid = isValid
                    this.indicators[instanceId].isFieldValid = isFieldValid
                    Alpine.$data(fieldEl).$dispatch('indicator-valid', { id: indicator.id, isValid: isFieldValid })

                    updated = true
                }
                // Check if formula is dependant
                if (!indicator.is_direct_indicator && indicator.formula.includes(code)) {
                    // If calculating set total, remove instance number
                    if (indicator.formula.includes("set")) {
                        instanceId = indicator.id
                    }
                    const value = this.evaluateExpression(indicator.formula, instanceId, indicator.code)
                    if (value != null) {
                        if (value == '__copy__') {
                            this.indicators[instanceId].value = this.indicators[instanceId].value
                            const indicatorToCopy = this.getIndicatorDataByCode(code)
                            // If the field to copy has options copy them
                            if (this.hasOptions(indicatorToCopy.data_type)) {
                                const fieldEl = document.getElementById(`question_${indicator.id}`)
                                Alpine.$data(fieldEl).copyFieldOptions(indicatorToCopy.id)
                            }
                        } else if (indicator.data_type == this.fieldTypes.BOOLEAN) {
                            if (value === true) {
                                this.indicators[instanceId].value = 'True'
                            } else if (value === false) {
                                this.indicators[instanceId].value = 'False'
                            }
                        } else if (indicator.data_type == this.fieldTypes.DECIMAL) {
                            this.indicators[instanceId].value = String((Math.round(value * 100) / 100).toFixed(2))
                        } else {
                            this.indicators[instanceId].value = String(value)
                        }
                    }

                    // Update validation
                    const { isValid, isFieldValid } = this.validateField(instanceId)
                    this.indicators[instanceId].isValid = isValid
                    this.indicators[instanceId].isFieldValid = isFieldValid
                    let fieldEl = document.querySelector(`#field_${instanceId}`);
                    Alpine.$data(fieldEl).updateErrors(isFieldValid)
                    Alpine.$data(fieldEl).$dispatch('indicator-valid', { id: indicator.id, isValid: isFieldValid })

                    updated = true
                }
                if (indicator.validation.includes(code)) {
                    if (indicator.is_group_indicator) {
                        this.validateField(instanceId, '', '', false, true)
                    } else {
                        const { isValid, isFieldValid } = this.validateField(instanceId)
                        if (!indicator.is_direct_indicator) {
                            let fieldEl = document.querySelector(`#field_${instanceId}`);
                            Alpine.$data(fieldEl).updateErrors(isFieldValid)
                        }
                    }

                    updated = true
                }
                if (updated) {
                    this.updateIndicatorDependencies(instanceId)
                }
            } else {
                const indicatorsSet = this.indicatorsSets.find(s => s.code == dependantIndicatorCode)
                // Update conditional set
                if (indicatorsSet && indicatorsSet.condition.includes(code)) {
                    const setEl = document.querySelector(`#set_${indicatorsSet.id}`);
                    const show = this.isVisible("", indicatorsSet.condition)
                    Alpine.$data(setEl).updateShow(show)
                }
            }
        },
        isGendered(type) {
            switch (type) {
                case this.fieldTypes.INTEGERGENDER:
                case this.fieldTypes.DECIMALGENDER:
                    return true
                default:
                    return false
            }
        },
        isNumeric(type) {
            switch (type) {
                case this.fieldTypes.STRING:
                case this.fieldTypes.TEXT:
                case this.fieldTypes.BOOLEAN:
                case this.fieldTypes.DATE:
                case this.fieldTypes.DROPDOWN:
                case this.fieldTypes.CHECKBOX:
                case this.fieldTypes.RADIOBUTTON:
                    return false
                case this.fieldTypes.INTEGER:
                case this.fieldTypes.DECIMAL:
                case this.fieldTypes.INTEGERGENDER:
                case this.fieldTypes.DECIMALGENDER:
                    return true
                default:
                    console.log(type, "No matching type found")
                    return false
            }
        },
        hasOptions(type) {
            switch (type) {
                case this.fieldTypes.STRING:
                case this.fieldTypes.TEXT:
                case this.fieldTypes.INTEGER:
                case this.fieldTypes.DECIMAL:
                case this.fieldTypes.BOOLEAN:
                case this.fieldTypes.INTEGERGENDER:
                case this.fieldTypes.DECIMALGENDER:
                case this.fieldTypes.DATE:
                    return false
                case this.fieldTypes.DROPDOWN:
                case this.fieldTypes.CHECKBOX:
                case this.fieldTypes.RADIOBUTTON:
                    return true
                default:
                    console.log(type, "No matching type found")
                    return false
            }
        },
        isMultiAnswer(type) {
            switch (type) {
                case this.fieldTypes.STRING:
                case this.fieldTypes.TEXT:
                case this.fieldTypes.INTEGER:
                case this.fieldTypes.DECIMAL:
                case this.fieldTypes.DROPDOWN:
                case this.fieldTypes.RADIOBUTTON:
                case this.fieldTypes.BOOLEAN:
                case this.fieldTypes.INTEGERGENDER:
                case this.fieldTypes.DECIMALGENDER:
                case this.fieldTypes.DATE:
                    return false
                case this.fieldTypes.CHECKBOX:
                    return true
                default:
                    console.log(type, "No matching type found")
                    return false
            }
        },
        getInstanceId(code, referenceInstanceId = '') {
            let instanceId = this.getIndicatorDataByCode(code).id
            if (referenceInstanceId.includes("_")) {
                const instanceIdTokens = referenceInstanceId.split("_")
                const instanceNumber = instanceIdTokens.length == 2 ? instanceIdTokens[1] : -1
                instanceId = instanceId + "_" + instanceNumber
            }
            return instanceId
        },
        belongsToSet(code) {
            let index
            for (let i = 0; i < this.indicatorsSets.length; i++) {
                index = this.indicatorsSets[i].indicators_ids.findIndex(id => id == this.indicatorIdByCode[code])
                if (index != -1) { break }
            }
            return index != -1
        },
        storeMaps() {
            this.indicatorsData.forEach((i, index) => {
                this.indicatorDataIndexById[i.id] = index
                this.indicatorDataIndexByCode[i.code] = index
                this.indicatorIdByCode[i.code] = i.id
            })
        },
        getIndicatorDataById(id) {
            try {
                return this.indicatorsData[this.indicatorDataIndexById[id]]
            } catch {
                return null
            }
        },
        getIndicatorDataByCode(code) {
            try {
                return this.indicatorsData[this.indicatorDataIndexByCode[code]]
            } catch {
                return null
            }
        }
    })


    if (document.getElementById('indicatorResults')) {
        const indicatorResults = JSON.parse(document.getElementById('indicatorResults').textContent);
        Alpine.store('indicators')["indicatorResults"] = indicatorResults
    }
    if (document.getElementById('placeholders')) {
        const placeholders = JSON.parse(document.getElementById('placeholders').textContent);
        Alpine.store('indicators')["placeholders"] = placeholders
    }
    if (document.getElementById('indicatorsSets')) {
        const indicatorsSets = JSON.parse(document.getElementById('indicatorsSets').textContent);
        Alpine.store('indicators')["indicatorsSets"] = indicatorsSets
    }
    if (document.getElementById('indicators')) {
        const indicators = JSON.parse(document.getElementById('indicators').textContent);
        Alpine.store('indicators').initIndicators(indicators)
    }

}

if (document.readyState === "complete" && Alpine) {
    initIndicatorsStore()
} else {
    document.addEventListener('alpine:init', initIndicatorsStore)
}