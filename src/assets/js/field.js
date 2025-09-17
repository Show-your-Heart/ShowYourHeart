
document.addEventListener('alpine:init', () => {
    Alpine.data('field', (code = "") => ({
        id: "",
        name: "",
        code: "",
        value: "",
        isDirectIndicator: true,
        condition: "",
        formula: "",
        validation: "",
        msg: "",
        hasErrors: false,
        error: "",
        show: true,
        init() {
            console.log("Initializing field", code)
            const indicator = Alpine.store('survey')["indicators"].find(i => i.code == code)
            console.log("Got indicator", indicator)
            this.id = indicator.id
            this.name = indicator.name
            this.code = indicator.code
            this.isDirectIndicator = indicator.is_direct_indicator
            if (indicator.is_direct_indicator) {
                this.condition = indicator.condition
                this.validation = indicator.validation
            } else {
                this.formula = indicator.formula
            }
            this.msg = indicator.message
            console.log("Check condition", indicator.condition)
            // this.show = (indicator.condition == "" || Alpine.store('survey').isVisible(indicator))
            this.show = indicator.is_direct_indicator && (indicator.condition == "" || Alpine.store('survey').isVisible(indicator))
        },
        update(event) {
            try {
                this.value = event.target.value
                const field = {
                    code: this.code,
                    value: this.value,
                    validation: this.validation,
                }
                isValid = Alpine.store('survey').isValid(field)
                if (isValid.error == undefined && isValid) {
                    console.log('correcto')
                    this.hasErrors = false
                    Alpine.store('survey').updateIndicatorResult(this.code, this.value)
                } else {
                    this.hasErrors = true
                    this.error = `Value its incorrect, has to meet condition: '${this.validation}'`
                }
            } catch (e) {
                console.log('incorrecto')
                console.log(e)
                this.hasErrors = true
                this.error = e.message
            }
        }
    }))

    // }
})