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
        placeholder: "",
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
        unit: "",
        mandatory: false,
        init() {
            const indicator = Alpine.store('indicators')["indicators"].find(i => i.code == code)
            const initialValue = Alpine.store('indicators')["initialValues"][code] || null
            this.id = indicator.id
            this.name = indicator.name
            this.description = indicator.description
            this.code = indicator.code
            this.type = indicator.data_type
            this.unit = indicator.unit
            this.mandatory = indicator.mandatory
            this.value = this.loadInitialValue(initialValue?.[0] ?? null, indicator.data_type)
            this.not_applicable = initialValue?.[1] ?? false
            // this.placeholder = this.loadInitialPlaceholder(initialPlaceholder, indicator.data_type)
            Alpine.store('indicators').shallowIndicatorResultUpdate(this.code, this.value)
            this.isDirectIndicator = indicator.is_direct_indicator
            this.required = indicator.required
            if (indicator.is_direct_indicator) {
                this.condition = indicator.condition
                this.validation = indicator.validation
            } else {
                this.formula = indicator.formula
            }
            this.msg = indicator.message
            this.show = indicator.is_direct_indicator && (indicator.condition == "" || Alpine.store('indicators').isVisible(indicator))
            const field = {
                id: this.id,
                code: this.code,
                value: this.value,
                validation: this.validation,
            }
            isValid = Alpine.store('indicators').validate(field)
            if (isValid && isValid.error == undefined) {
                this.hasErrors = false
            } else {
                this.hasErrors = true
                this.error = `Value its incorrect, has to meet condition: '${this.validation}'`
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
            } else if (this.isGendered(type)) {
                if (initialValue && initialValue.female) {
                    value = {
                        female: initialValue.female,
                        male: initialValue.male,
                        nonBinary: initialValue.non_binary,
                    }
                } else {
                    value = {
                        female: 0,
                        male: 0,
                        nonBinary: 0,
                    }
                }
            } else {
                value = initialValue
            }
            return value
        },
        update(event, subtype = "") {
            try {
                this.value = this.updateValue(event.target.value, this.value, this.type, subtype)
                const field = {
                    id: this.id,
                    code: this.code,
                    value: this.value,
                    validation: this.validation,
                }
                isValid = Alpine.store('indicators').validate(field)
                if (isValid && isValid.error == undefined) {
                    console.log('Valido', this.value)
                    this.hasErrors = false
                    Alpine.store('indicators').updateIndicatorResult(this.code, this.value)
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
        updateValue(input, current, type, subtype = "") {
            if (!current) return ""
            let value = ""
            if (this.isMultiAnswer(type)) {
                const index = current.findIndex(v => v == input)
                value = current
                if (index != -1) {
                    value.splice(index, 1)
                } else {
                    value.push(input)
                }
            } else if (this.isGendered(type)) {
                value = current
                value[subtype] = input
            } else {
                value = input
            }
            return value
        },
        isGendered(type) {
            switch (type) {
                case FieldType.INTEGERGENDER:
                case FieldType.DECIMALGENDER:
                    return true
                default:
                    return false
            }
        },
        hasOptions(type) {
            switch (type) {
                case FieldType.STRING:
                case FieldType.TEXT:
                case FieldType.INTEGER:
                case FieldType.DECIMAL:
                case FieldType.BOOLEAN:
                case FieldType.INTEGERGENDER:
                case FieldType.DECIMALGENDER:
                case FieldType.DATE:
                    return false
                case FieldType.DROPDOWN:
                case FieldType.CHECKBOX:
                case FieldType.RADIOBUTTON:
                    return true
                default:
                    console.log(type, "No matching type found")
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
                case FieldType.INTEGERGENDER:
                case FieldType.DECIMALGENDER:
                case FieldType.DATE:
                    return false
                case FieldType.CHECKBOX:
                    return true
                default:
                    console.log(type, "No matching type found")
                    return false
            }
        },


    }))
})