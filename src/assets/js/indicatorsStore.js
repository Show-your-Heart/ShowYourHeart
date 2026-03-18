/* 
    Indicator state
    {
        value
        show
        notApplicable
        isValid
        isFieldValid
        hasErrors
        error
    }
*/

const initIndicatorsStore = () => {
    Alpine.store('indicators', {
        indicators: {},
        indicatorsResults: [],
        indicatorsData: [],
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
            indicators.forEach(i => this.indicators[i.code] = {
                value: '',
                show: false,
                notApplicable: false,
                isValid: false,
                isFieldValid: false,
                hasErrors: false,
                error: '',
            })
            this.indicatorsData = indicators
        },
        parseExpression(expr, val) {
            const tokens = expr.split(" ")

            let loadedTokens = []
            for (let token of tokens) {
                let value = null
                if (token.match(/^[a-zA-Z]\w*/)) {
                    if (token.match(/(_)/)) {
                        // Reference to other group indicator
                        const subtokens = token.split("_")
                        if (subtokens.includes('total')) {
                            // Load list or table column total
                            value = this.loadTotalIndicatorResult(subtokens)
                        } else {
                            value = subtokens.length == 2 ? this.loadIndicatorResult(subtokens[0], subtokens[1]) : this.loadIndicatorResult(subtokens[0], subtokens[1], subtokens[2])
                        }
                    } else if (token == 'val' && val.match(/(_)/)) {
                        // Reference to current group indicator
                        const subtokens = val.split("_")
                        value = subtokens.length == 2 ? this.loadIndicatorResult(subtokens[0], subtokens[1]) : this.loadIndicatorResult(subtokens[0], subtokens[1], subtokens[2])
                    } else if (token == 'val') {
                        // Reference to other indicator 
                        value = this.loadIndicatorResult(val)
                    } else if (token == 'AND' || token == 'and') {
                        value = '&&'
                    } else if (token == 'OR' || token == 'or') {
                        value = '||'
                    } else {
                        // Reference to current indicator
                        value = this.loadIndicatorResult(token)
                    }
                    if (value == undefined) {
                        throw new Error(`Missing value, please fill question ${token} before.`)
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
            console.log("Parsed expression: ")
            console.log("  expression --> ", expr)
            console.log(" js parsed expression --> ", jsExpr)

            return jsExpr
        },
        evaluateExpression(expr, val = '') {
            try {
                const parsedExpression = this.parseExpression(expr, val)
                return eval(parsedExpression)
            } catch (e) {
                throw e
            }
        },
        validateField(code, suffix = '', suffix2 = '', validateGroupItem = false, setGroupItems = false) {

            console.log("validating...", code, this.indicators[code].value)

            const indicator = this.indicatorsData.find(i => i.code == code)

            let result = {
                isValid: true,
                isFieldValid: true
            }

            let fieldEl = null
            let fieldData = null
            if (setGroupItems) {
                fieldEl = document.querySelector(`#field-${indicator.id}`)
                fieldData = Alpine.$data(fieldEl)
            }

            if (this.indicators[code].notApplicable) {
                console.log("not applicable")
                return result
            }

            // Simple fields without validation expression are true when a value is assigned
            if (
                (indicator.validation == '' && this.indicators[code].value !== null && this.indicators[code].value !== "" && !(this.indicators[code].value instanceof Object)) ||
                (indicator.validation == '' && this.indicators[code].value instanceof Object && !indicator.is_group_indicator && (this.indicators[code].value.value !== undefined || this.indicators[code].value.female !== undefined))
            ) {
                console.log("simple field filled without validation ")
                return result
            }

            // Empty non mandatory fields
            if (
                !indicator.mandatory && // Non mandatory
                (this.indicators[code].value == null || this.indicators[code].value == "" || // Empty string or number
                    (this.indicators[code].value instanceof Object && !indicator.is_group_indicator &&  // Object value butno group indicator
                        (this.indicators[code].value.value == null || this.indicators[code].value.female == null) // Dropdown/checkbock or gendered field
                    )
                )
            ) {
                console.log("Empty non mandatory simple field filled")
                return result
            }

            try {
                if (indicator.is_group_indicator && !Array.isArray(this.indicators[code].value) && this.indicators[code].value !== null) {
                    // Validate lists and tables
                    result.isValid = this.indicators[code].isValid instanceof Object ? this.indicators[code].isValid : {}

                    if (indicator.group_2_items) {
                        indicator.group_items.forEach(({ suffix: k }) => {
                            if (result.isValid[k] == undefined) {
                                result.isValid[k] = {}
                            }
                            indicator.group_2_items.forEach(({ suffix: k2 }) => {
                                // Only validate for the current groupItem or if the whole field has to be validated
                                if (!validateGroupItem || (validateGroupItem && `${code}_${k}_${k2}` == `${code}_${suffix}_${suffix2}`)) {
                                    if (!indicator.mandatory && (this.indicators[code].value[k][k2] === null || this.indicators[code].value[k][k2] === '')) {
                                        // Empty non mandatory is valid
                                        result.isValid[k][k2] = true
                                    } else if (indicator.mandatory && (this.indicators[code].value[k][k2] === null || this.indicators[code].value[k][k2] === '')) {
                                        // Empty mandatory is not valid
                                        result.isValid[k][k2] = false
                                        console.log("Empty mandatory is not valid", this.indicators[code].value[k][k2])

                                    } else {
                                        result.isValid[k][k2] = indicator.validation == '' ? true : !!this.evaluateExpression(indicator.validation, `${code}_${k}_${k2}`)
                                        console.log("got to else", result.isValid[k][k2])
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
                                if (!indicator.mandatory && (this.indicators[code].value[k] === null || this.indicators[code].value[k] === '')) {
                                    // Empty non mandatory is valid
                                    result.isValid[k] = true
                                } else if (indicator.mandatory && (this.indicators[code].value[k] === null || this.indicators[code].value[k] === '')) {
                                    // Empty mandatory is not valid
                                    result.isValid[k] = false
                                } else {
                                    result.isValid[k] = indicator.validation == '' ? true : !!this.evaluateExpression(indicator.validation, `${code}_${k}`)
                                    // console.log("sechk it out!", result.isValid)
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
                    console.log("is group", result.isValid)
                } else {
                    console.log("validate simple field expression", indicator.validation)
                    // Validate simple indicators
                    result.isValid = !!this.evaluateExpression(indicator.validation, code)
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
        isVisible(code, condition) {
            try {
                return this.evaluateExpression(condition, code)
            } catch (e) {
                return false
            }
        },
        loadIndicatorResult(code, suffix = "", suffix2 = "") {
            let result = null
            const indicator = this.indicatorsData.find(i => i.code == code)

            if (this.hasOptions(indicator.data_type)) {
                if (this.isMultiAnswer(indicator.data_type)) {
                    result = this.indicators[code].value.map(v => v.value)
                } else {
                    result = this.indicators[code].value.value
                }
            } else if (indicator.data_type == this.fieldTypes.BOOLEAN) {
                result = this.indicators[code].value == 'True' ? 'true' : 'false'
            } else if (suffix != "") {
                if (suffix2 == "") {
                    switch (suffix) {
                        case 'men':
                            result = Number(indicator.value.male)
                            break;
                        case 'women':
                            result = Number(indicator.value.female)
                            break;
                        case 'nb':
                            result = Number(indicator.value.nonBinary)
                            break;
                        case 'total':
                            result = Object.keys(indicator.value).reduce((prev, k) => prev + Number(indicator.value[k]), 0)
                            break;
                        default:
                            result = this.indicators[code].value[suffix]
                    }
                } else {
                    result = this.indicators[code].value[suffix][suffix2]
                }

            } else {
                result = this.indicators[code].value || null
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
        loadTotalIndicatorResult(subtokens) {
            let result = null
            if (subtokens.length == 2) {
                // List or table total
                console.log("Loading total:", this.indicators[subtokens[0]].value)
                result = this.indicators[subtokens[0]].value.total
            } else if (subtokens.length == 3) {
                // Table row or column total
                console.log("Loading total:", subtokens, this.indicators[subtokens[0]].value)
                result = this.indicators[subtokens[0]].value[subtokens[1]].total
            } else {
                console.log("Invalid total token ")
                result = 0
            }
            return result
        },
        updateIndicatorDependencies(code) {
            const index = this.indicatorsData.findIndex(i => i.code == code)
            if (index != -1 && this.indicatorsData[index].dependant_indicators) {
                for (dependantIndicatorCode of this.indicatorsData[index].dependant_indicators) {
                    this.updateDependantIndicator(dependantIndicatorCode, code)
                }
            }
        },
        updateDependantIndicator(dependantIndicatorCode, code) {
            const index = this.indicatorsData.findIndex(i => i.code == dependantIndicatorCode)
            if (index != -1) {
                let indicator = this.indicatorsData[index]

                // Check which expressions are dependent of this indicator
                // Check if condition is dependant
                if (indicator.condition.includes(code)) {
                    const fieldEl = document.querySelector(`#field-${indicator.id}`);
                    const show = this.isVisible(indicator.code, indicator.condition)
                    Alpine.$data(fieldEl).updateShow(show)

                    // Hide direct indicator and set NA 
                    if (indicator.is_direct_indicator && !show) {
                        this.updateIndicatorResultNa(indicator.code, true, true)
                    }

                    // Update validation
                    const { isValid, isFieldValid } = this.validateField(dependantIndicatorCode)
                    this.indicators[dependantIndicatorCode].isValid = isValid
                    this.indicators[dependantIndicatorCode].isFieldValid = isFieldValid
                    Alpine.$data(fieldEl).$dispatch('indicator-valid', { id: indicator.id, isValid: isFieldValid })

                }
                // Check if formula is dependant
                if (!indicator.is_direct_indicator && indicator.formula.includes(code)) {
                    const value = this.evaluateExpression(indicator.formula, indicator.code)
                    if (value != null) {
                        const fieldEl = document.querySelector(`#question_${indicator.id}`);
                        fieldEl && (this.indicators[dependantIndicatorCode].value = String(value))
                    }
                }
                // TODO: Check if validation is dependant
                if (indicator.validation.includes(code)) {
                    console.log("TODO: Run dependant validation")
                }
            }
        },
        updateIndicatorResultNa(code, value, hide = false) {
            this.indicators[code].notApplicable = value

            if (hide) {
                this.indicators[code].show = !value
            }

            const indicator = this.indicatorsData.find(i => i.code == code)
            if (indicator.dependant_indicators) {
                for (code of indicator.dependant_indicators) {
                    this.updateIndicatorResultNa(code, value, true)
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
    })

    if (document.getElementById('indicators')) {
        const indicators = JSON.parse(document.getElementById('indicators').textContent);
        Alpine.store('indicators').initIndicators(indicators)
    }
    if (document.getElementById('indicatorResults')) {
        const indicatorResults = JSON.parse(document.getElementById('indicatorResults').textContent);
        Alpine.store('indicators')["indicatorResults"] = indicatorResults
    }
    if (document.getElementById('placeholders')) {
        const placeholders = JSON.parse(document.getElementById('placeholders').textContent);
        Alpine.store('indicators')["placeholders"] = placeholders
    }

}

if (document.readyState === "complete" && Alpine) {
    initIndicatorsStore()
} else {
    document.addEventListener('alpine:init', initIndicatorsStore)
}