const FieldType = {
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
}

document.addEventListener('alpine:init', () => {
    Alpine.data('field', (code = "") => ({
        id: "",
        name: "",
        description: "",
        code: "",
        value: "",
        type: "",
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
            const indicator = Alpine.store('survey')["indicators"].find(i => i.code == code)
            const initialValue = Alpine.store('survey')["initialValues"][code] || null
            this.id = indicator.id
            this.name = indicator.name
            this.description = indicator.description
            this.code = indicator.code
            this.type = indicator.data_type
            this.value = this.loadInitialValue(initialValue, indicator.data_type)
            Alpine.store('survey').shallowIndicatorResultUpdate(this.code, this.value)
            this.isDirectIndicator = indicator.is_direct_indicator
            this.required = indicator.required
            if (indicator.is_direct_indicator) {
                this.condition = indicator.condition
                this.validation = indicator.validation
            } else {
                this.formula = indicator.formula
            }
            this.msg = indicator.message
            this.show = indicator.is_direct_indicator && (indicator.condition == "" || Alpine.store('survey').isVisible(indicator))
        },
        update(event) {
            try {
                this.value = this.updateValue(event.target.value, this.value, this.type)
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
        },
        loadInitialValue(initialValue, type) {
            let value = ""
            if (this.hasOptions(type)) {
                if (initialValue) {
                    value = initialValue.split("|")
                } else {
                    value = []
                }
            } else {
                value = initialValue
            }
            return value
        },
        hasOptions(type) {
            switch (type) {
                case FieldType.STRING:
                case FieldType.TEXT:
                case FieldType.INTEGER:
                case FieldType.DECIMAL:
                case FieldType.BOOLEAN:
                    return false
                case FieldType.DROPDOWN:
                case FieldType.CHECKBOX:
                case FieldType.RADIOBUTTON:
                    return true
                default:
                    console.log("No matching type found")
                    return false
            }
        },
        isMultiAnswer(type) {
            switch (type) {
                case FieldType.STRING:
                case FieldType.TEXT:
                case FieldType.INTEGER:
                case FieldType.DECIMAL:
                case FieldType.DROPDOWN:
                case FieldType.RADIOBUTTON:
                case FieldType.BOOLEAN:
                    return false
                case FieldType.CHECKBOX:
                    return true
                default:
                    console.log("No matching type found")
                    return false
            }
        },
        updateValue(input, current, type) {
            let value = ""
            if (this.isMultiAnswer(type)) {
                const index = current.findIndex(v => v == input)
                value = current
                if (index != -1) {
                    value.splice(index, 1)
                } else {
                    value.push(input)
                }
            } else {
                value = input
            }
            return value
        },

    }))
})