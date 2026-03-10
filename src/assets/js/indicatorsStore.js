const initIndicatorsStore = () => {
    Alpine.store('indicators', {
        indicators: [],
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
        validateField(field, validateGroupItem = false, setGroupItems = false) {

            let result = {
                isValid: true,
                isFieldValid: true
            }

            let fieldEl = null
            let fieldData = null
            if (setGroupItems) {
                fieldEl = document.querySelector(`#field-${field.id}`)
                fieldData = Alpine.$data(fieldEl)
            }

            if (field.notApplicable) {
                Alpine.store("survey").setIndicatorValidation(field.id, true)
                return result
            }
            // Simple fields without validation expression are true when a value is assigned
            if (
                (!field.validation && field.value != null && field.value != "" && !(field.value instanceof Object)) ||
                (!field.validation && field.value instanceof Object && !field.isGroupIndicator && field.value.value)
            ) {
                Alpine.store("survey").setIndicatorValidation(field.id, true)
                return result
            }
            try {
                if (field.isGroupIndicator && !Array.isArray(field.value) && field.value !== null) {
                    // Validate lists and tables
                    const indicator = this.indicators.find(i => i.id == field.id)
                    result.isValid = field.isValid

                    if (indicator.group_2_items) {
                        indicator.group_items.forEach(({ suffix: k }) => {
                            if (result.isValid[k] == undefined) {
                                result.isValid[k] = {}
                            }
                            indicator.group_2_items.forEach(({ suffix: k2 }) => {
                                // Only validate for the current groupItem or if the whole field has to be validated
                                if (!validateGroupItem || (validateGroupItem && `${indicator.code}_${k}_${k2}` == field.code)) {
                                    result.isValid[k][k2] = field.validation == '' && field.value[k][k2] != null ? true : this.evaluateExpression(field.validation, `${indicator.code}_${k}_${k2}`)
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
                            if (!validateGroupItem || (validateGroupItem && `${indicator.code}_${k}` == field.code)) {
                                result.isValid[k] = field.validation == '' && field.value[k] != null ? true : this.evaluateExpression(field.validation, `${indicator.code}_${k}`)
                            }
                            if (!result.isValid[k]) {
                                result.isFieldValid = false
                            }
                            if (setGroupItems) {
                                fieldData.setGroupItemValid(k)
                            }
                        })
                    }
                    Alpine.store("survey").setIndicatorValidation(field.id, result.isFieldValid)
                } else {
                    // Validate simple indicators
                    result.isValid = !!this.evaluateExpression(field.validation, field.code)
                    result.isFieldValid = result.isValid
                    Alpine.store("survey").setIndicatorValidation(field.id, result.isValid)
                }
                return result
            } catch (e) {
                Alpine.store("survey").setIndicatorValidation(field.id, false)
                return {
                    isValid: false,
                    isFieldValid: false
                }
            }
        },
        isVisible(indicator) {
            try {
                return this.evaluateExpression(indicator.condition, indicator.code)
            } catch (e) {
                return false
            }
        },
        loadIndicatorResult(code, suffix = "", suffix2 = "") {
            let result = null
            const indicator = this.indicators.find(i => i.code == code)

            if (this.hasOptions(indicator.data_type)) {
                const fieldEl = document.querySelector(`#question_${indicator.id}`);
                const fieldData = Alpine.$data(fieldEl)
                if (this.isMultiAnswer(indicator.data_type)) {
                    result = fieldData.value.map(v => v.value)
                } else {
                    result = fieldData.value.value
                }
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
                            result = indicator.value[suffix]
                    }
                } else {
                    result = indicator.value[suffix][suffix2]
                }

            } else {
                result = indicator.value || null
            }

            if (indicator.mandatory) {
                const na_element = document.getElementById(`question_${indicator.id}_na`)
                if (na_element.checked)
                    result = 0
            }

            if (result == null || (indicator.data_type != this.fieldTypes.STRING && result == "")) {
                result = 'null'
            }

            return result
        },
        loadTotalIndicatorResult(subtokens) {
            let result = null
            const indicator = this.indicators.find(i => i.code == subtokens[0])

            if (indicator.group_2_id == null) {
                // List total
                result = Object.keys(indicator.value).reduce((prev, k) => prev + Number(indicator.value[k]), 0)
            } else if (indicator.group_2_items.length > 0) {
                const columnIndex = indicator.group_2_items.findIndex(i => i.suffix == subtokens[1])
                if (columnIndex == -1) {
                    // Table row total
                    result = indicator.group_2_items.reduce((prev, i) => prev + Number(indicator.value[subtokens[1]][i.suffix]), 0)
                } else {
                    // Table column total
                    result = Object.keys(indicator.value).reduce((prev, k) => prev + Number(indicator.value[k][subtokens[1]]), 0)
                }
            } else {
                console.log("Invalid total token ")
                result = 0
            }
            return result
        },
        shallowIndicatorResultUpdate(code, value, notApplicable) {
            const index = this.indicators.findIndex(i => i.code == code)
            this.indicators[index].value = value
            this.indicators[index].not_applicable = notApplicable
        },
        updateIndicatorResult(code, value) {
            const index = this.indicators.findIndex(i => i.code == code)
            if (index != -1) {
                this.indicators[index].value = value
                if (this.indicators[index].dependant_indicators) {
                    for (code of this.indicators[index].dependant_indicators) {
                        this.updateDependantIndicator(code)
                    }
                }
            }
        },
        updateDependantIndicator(code) {
            const index = this.indicators.findIndex(i => i.code == code)
            if (index != -1) {
                let indicator = this.indicators[index]
                if (indicator.is_direct_indicator) {
                    const show = indicator.condition == "" || this.isVisible(indicator)
                    if (!show) {
                        this.updateIndicatorResultNa(code, !show, true)
                    } else {
                        const fieldEl = document.querySelector(`#field-${indicator.id}`);
                        Alpine.$data(fieldEl).show = show
                        Alpine.$data(fieldEl).notApplicable = !show
                    }
                } else {
                    const value = this.evaluateExpression(indicator.formula, indicator.code)
                    if (value != null) {
                        const fieldEl = document.querySelector(`#question_${indicator.id}`);
                        fieldEl && (Alpine.$data(fieldEl).value = String(value))
                    }
                }
            }
        },
        updateIndicatorResultNa(code, value, hide = false) {
            const index = this.indicators.findIndex(i => i.code == code)
            if (index != -1) {
                let indicator = this.indicators[index]
                this.indicators[index].not_applicable = value

                const fieldEl = document.querySelector(`#field-${indicator.id}`);
                if (hide) {
                    Alpine.$data(fieldEl).show = !value
                }
                Alpine.$data(fieldEl).notApplicable = value

                if (indicator.dependant_indicators) {
                    for (code of indicator.dependant_indicators) {
                        this.updateIndicatorResultNa(code, value, true)
                    }
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
        Alpine.store('indicators')["indicators"] = indicators
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