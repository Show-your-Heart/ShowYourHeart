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
        parseExpression(expr, code = '') {
            const tokens = expr.split(" ")

            let loadedTokens = []
            for (let token of tokens) {
                let value = null
                if (token.match(/^[a-zA-Z]\w*/)) {
                    if (token.match(/(_)/)) {
                        // Reference to other group indicator
                        const subtokens = token.split("_")
                        value = subtokens.length == 2 ? this.loadIndicatorResult(subtokens[0], subtokens[1]) : this.loadIndicatorResult(subtokens[0], subtokens[1], subtokens[2])
                    } else if (token == 'val' && code.match(/(_)/)) {
                        // Reference to current group indicator
                        const subtokens = code.split("_")
                        value = subtokens.length == 2 ? this.loadIndicatorResult(subtokens[0], subtokens[1]) : this.loadIndicatorResult(subtokens[0], subtokens[1], subtokens[2])
                    } else if (token == 'val') {
                        value = this.loadIndicatorResult(code)
                        // Reference to other indicator 
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
        evaluateExpression(expr) {
            try {
                return eval(expr)
            } catch (e) {
                throw e
            }
        },
        validate(field) {
            if (field.notApplicable) {
                Alpine.store("survey").setIndicatorValidation(field.id, true)
                return true
            }
            if (!field.validation && field.value != null && field.value != "") {
                Alpine.store("survey").setIndicatorValidation(field.id, true)
                return true
            }
            try {
                parsedExpression = this.parseExpression(field.validation, field.code)
                result = this.evaluateExpression(parsedExpression)
                Alpine.store("survey").setIndicatorValidation(field.id, !!result)
                return result
            } catch (e) {
                Alpine.store("survey").setIndicatorValidation(field.id, false)
                return false
            }
        },
        isVisible(indicator) {
            try {
                parsedExpression = this.parseExpression(indicator.condition, indicator.code)
                return this.evaluateExpression(parsedExpression)
            } catch (e) {
                return false
            }
        },
        computeFormula(indicator) {
            try {
                parsedExpression = this.parseExpression(indicator.formula, indicator.code)
                return this.evaluateExpression(parsedExpression)
            } catch (e) {
                return null
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
                    const fieldEl = document.querySelector(`#field-${indicator.id}`);
                    Alpine.$data(fieldEl).show = show
                    Alpine.$data(fieldEl).notApplicable = !show
                } else {
                    const value = this.computeFormula(indicator)
                    if (value != null) {
                        const fieldEl = document.querySelector(`#question_${indicator.id}`);
                        fieldEl && (Alpine.$data(fieldEl).value = String(value))
                    }
                }
            }
        },
        updateIndicatorResultNa(code, value) {
            const index = this.indicators.findIndex(i => i.code == code)
            if (index != -1) {
                this.indicators[index].not_applicable = value
                /*  if (indicators[index].dependant_indicators) {
                     for (code of this.indicators[index].dependant_indicators) {
                         this.updateIndicatorResultNa(code, value)
                     }
                 } */
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

}

if (document.readyState === "complete" && Alpine) {
    initIndicatorsStore()
} else {
    document.addEventListener('alpine:init', initIndicatorsStore)
}