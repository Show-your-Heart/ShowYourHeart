document.addEventListener('alpine:init', () => {
    Alpine.store('survey', {
        indicators: [],
        parseExpression(expr, currentIndicatorCode = "", currentIndicatorValue = 0) {
            const tokens = expr.split(" ")

            let loadedTokens = []
            for (let token of tokens) {
                if (token.match(/^[a-zA-Z_]\w*$/)) {
                    // If current indicator, get value from params
                    if (token == currentIndicatorCode) {
                        loadedTokens.push(currentIndicatorValue)
                        // If reference to another indicator, get value from global state
                    } else {
                        const value = this.loadIndicatorResult(token)
                        if (value == undefined) {
                            throw new Error(`Missing value, please fill question ${token} before.`)
                        }
                        loadedTokens.push(value)
                    }
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
        isValid(field) {
            if (!field.validation) {
                return true
            }
            try {
                parsedExpression = this.parseExpression(field.validation, field.code, field.value)
                result = this.evaluateExpression(parsedExpression)
                return result
            } catch (e) {
                return false
            }
        },
        isVisible(indicator) {
            try {
                parsedExpression = this.parseExpression(indicator.condition, indicator.code, indicator.value)
                return this.evaluateExpression(parsedExpression)
            } catch (e) {
                console.log("Checking visibility of field failed", e)
                return false
            }
        },
        computeFormula(indicator) {
            try {
                parsedExpression = this.parseExpression(indicator.formula)
                return this.evaluateExpression(parsedExpression)
            } catch (e) {
                return null
            }
        },
        loadIndicatorResult(code) {
            return this.indicators.find(i => i.code == code).value || null
        },
        shallowIndicatorResultUpdate(code, value) {
            const index = this.indicators.findIndex(i => i.code == code)
            this.indicators[index].value = value
        },
        updateIndicatorResult(code, value) {
            const index = this.indicators.findIndex(i => i.code == code)
            this.indicators[index].value = value
            if (indicators[index].dependant_indicators) {
                for (code of indicators[index].dependant_indicators) {
                    this.updateDependantIndicator(code)
                }
            }
        },
        updateDependantIndicator(code) {
            console.log("Update dependant indicator:", code)
            const index = this.indicators.findIndex(i => i.code == code)
            let indicator = this.indicators[index]
            if (indicator.is_direct_indicator) {
                const show = indicator.condition == "" || this.isVisible(indicator)
                const fieldEl = document.querySelector(`#field-${indicator.id}`);
                Alpine.$data(fieldEl).show = show
            } else {
                const value = this.computeFormula(indicator)
                if (value != null) {
                    const fieldEl = document.querySelector(`#question_${indicator.id}`);
                    Alpine.$data(fieldEl).value = String(value)
                }
            }
        },
    })

    const indicators = JSON.parse(document.getElementById('indicators').textContent);
    Alpine.store('survey')["indicators"] = indicators
    const initialValues = JSON.parse(document.getElementById('initialValues').textContent);
    Alpine.store('survey')["initialValues"] = initialValues
})
