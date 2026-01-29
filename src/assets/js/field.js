const initFieldData = () => {
    Alpine.data('field', (code = "") => ({
        id: "",
        name: "",
        description: "",
        code: "",
        value: "",
        options: [],
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
        notApplicable: false,
        indicatorsStore: Alpine.store('indicators'),
        init() {
            const indicator = this.indicatorsStore["indicators"].find(i => i.code == code)
            const indicatorResults = this.indicatorsStore["indicatorResults"][code] || null
            this.id = indicator.id
            this.name = indicator.name
            this.description = indicator.description
            this.code = indicator.code
            this.type = indicator.data_type
            this.unit = indicator.unit
            this.mandatory = indicator.mandatory
            if (indicator.options) {
                this.options = indicator.options
            }
            this.value = this.loadInitialValue(indicatorResults?.value ?? null, indicator.data_type)
            this.notApplicable = indicatorResults?.not_applicable ?? false
            // this.placeholder = this.loadInitialPlaceholder(initialPlaceholder, indicator.data_type)
            this.indicatorsStore.shallowIndicatorResultUpdate(this.code, this.value, this.notApplicable)
            this.isDirectIndicator = indicator.is_direct_indicator
            this.required = indicator.required
            if (indicator.is_direct_indicator) {
                this.condition = indicator.condition
                this.validation = indicator.validation
            } else {
                this.formula = indicator.formula
            }
            this.msg = indicator.message
            this.show = indicator.is_direct_indicator && (indicator.condition == "" || this.indicatorsStore.isVisible(indicator))
            const field = {
                id: this.id,
                code: this.code,
                value: this.value,
                validation: this.validation,
                notApplicable: this.notApplicable,
            }
            isValid = this.indicatorsStore.validate(field)
        },
        loadInitialValue(initialValue, type) {
            let value = ""
            if (initialValue == null && this.indicatorsStore.isMultiAnswer(type)) {
                value = []
            }
            if (this.indicatorsStore.hasOptions(type)) {
                if (this.indicatorsStore.isMultiAnswer(type)) {
                    optionIds = initialValue.split("|")
                    value = optionIds.map(id => this.getOption(id))
                } else {
                    value = this.getOption(initialValue) || ""
                }
            } else if (this.indicatorsStore.isGendered(type)) {
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
            } else if (initialValue != null) {
                value = initialValue
            }
            return value
        },
        update(newValue, subtype = "") {
            try {
                this.value = this.updateValue(newValue, this.value, this.type, subtype)
                const field = {
                    id: this.id,
                    code: this.code,
                    value: this.value,
                    validation: this.validation,
                    notApplicable: this.notApplicable,
                }
                isValid = this.indicatorsStore.validate(field)
                if (isValid && isValid.error == undefined) {
                    this.hasErrors = false
                    this.indicatorsStore.updateIndicatorResult(this.code, this.value)
                } else {
                    this.hasErrors = true
                    if (this.msg) {
                        this.error = this.msg
                    } else if (this.validation == "") {
                        this.error = "Required field."
                    } else {
                        this.error = `Value it's incorrect, has to meet condition: '${this.validation}'`
                    }
                }
            } catch (e) {
                console.log('Invalido')
                console.log(e)
                this.hasErrors = true
                this.error = e.message
            }
        },
        updateValue(input, current, type, subtype = "") {
            // if (!current) return ""
            let value = ""
            if (this.indicatorsStore.hasOptions(type) && !this.indicatorsStore.isMultiAnswer(type)) {
                value = this.getOption(input)
            } else if (this.indicatorsStore.isMultiAnswer(type)) {
                //input is setted on the call to update from the x-effect of the component
                if (input && input.constructor == Array && input.length == 0) {
                    value = []
                } else {
                    const index = current.findIndex(v => v.id == input)
                    value = current
                    if (index != -1) {
                        value.splice(index, 1)
                    } else {
                        value.push(this.getOption(optionId))
                    }
                }
            } else if (this.indicatorsStore.isGendered(type)) {
                value = current
                value[subtype] = input
            } else {
                value = input
            }
            return value
        },
        updateNotApplicable(event) {
            this.notApplicable = event
            this.indicatorsStore.updateIndicatorResultNa(this.code, this.notApplicable)
            this.update("")
        },
        isOptionSelected(optionId) {
            if (this.indicatorsStore.isMultiAnswer(this.type)) {
                return !!this.value.find(v => v.id == optionId)
            }
            return this.value.id == optionId
        },
        getOption(id) {
            return this.options.find(o => o.id == id)
        }


    }))
}

if (document.readyState === "complete" && Alpine) {
    initFieldData()
} else {
    document.addEventListener('alpine:init', initFieldData)
}