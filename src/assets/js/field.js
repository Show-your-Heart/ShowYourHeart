
document.addEventListener('alpine:init', () => {
    Alpine.data('field', (code = "", value = "") => ({
        id: "",
        name: "",
        description: "",
        code: "",
        value: "",
        isDirectIndicator: true,
        required: true,
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
            this.description = indicator.description
            this.code = indicator.code
            this.value = value
            this.isDirectIndicator = indicator.is_direct_indicator
            this.required = indicator.required
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
                if (isValid && isValid.error == undefined) {
                    console.log('Valido', this.value)
                    this.hasErrors = false
                    Alpine.store('survey').updateIndicatorResult(this.code, this.value)
                } else {
                    this.hasErrors = true
                    this.error = `Value its incorrect, has to meet condition: '${this.validation}'`
                }
            } catch (e) {
                console.log('Invalido')
                console.log(e)
                this.hasErrors = true
                this.error = e.message
            }
        }
    }))
})