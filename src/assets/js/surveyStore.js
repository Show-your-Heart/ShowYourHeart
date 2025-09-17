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
            try {
                parsedExpression = this.parseExpression(field.validation, field.code, field.value)
                return this.evaluateExpression(parsedExpression)
            } catch (e) {
                return false
            }
        },
        isVisible(indicator) {
            try {
                parsedExpression = this.parseExpression(indicator.condition, indicator.code, indicator.value)
                return this.evaluateExpression(parsedExpression)
            } catch (e) {
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
        updateIndicatorResult(code, value) {
            const index = this.indicators.findIndex(i => i.code == code)
            this.indicators[index].value = value
            this.indicators = indicators
            for (code of indicators[index].dependant_indicators) {
                this.updateDependantIndicator(code)
            }
        },
        updateDependantIndicator(code) {
            console.log("Update dependant indicator:", code)
            const index = this.indicators.findIndex(i => i.code == code)
            let indicator = this.indicators[index]
            console.log(indicator)
            if (indicator.is_direct_indicator) {
                console.log("Is direct")
                const show = this.isVisible(indicator)
                const fieldEl = document.querySelector(`#field-${indicator.id}`);
                Alpine.$data(fieldEl).show = show
            } else {
                console.log("Is indirect")
                const value = this.computeFormula(indicator)
                if (value != null) {
                    const fieldEl = document.querySelector(`#field-${indicator.id}`);
                    Alpine.$data(fieldEl).value = value
                }
            }
        },

    })

    const indicators = JSON.parse(document.getElementById('indicators').textContent);
    Alpine.store('survey')["indicators"] = indicators
})
