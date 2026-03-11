const initFieldData = () => {
    Alpine.data('field', (code = "") => ({
        id: "",
        name: "",
        description: "",
        code: "",
        value: "",
        options: [],
        checkedOptions: [],
        placeholder: "",
        type: "",
        isDirectIndicator: true,
        isGroupIndicator: false,
        groupTitle: "",
        groupItems: [],
        groupTotal: false,
        group2Title: "",
        group2Items: [],
        group2Total: false,
        required: true,
        condition: "",
        formula: "",
        validation: "",
        isValid: false,
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
            this.placeholder = this.indicatorsStore["placeholders"][code] || null
            this.id = indicator.id
            this.name = indicator.name
            this.description = indicator.description
            this.code = indicator.code
            this.type = indicator.data_type
            this.unit = indicator.unit
            this.mandatory = indicator.mandatory
            this.isDirectIndicator = indicator.is_direct_indicator
            this.isGroupIndicator = indicator.is_group_indicator
            if (indicator.options) {
                this.options = indicator.options
            }
            if (indicator.is_group_indicator) {
                this.groupTitle = indicator.group_title
                this.groupItems = indicator.group_items
                this.groupTotal = indicator.group_total
                this.group2Title = indicator.group_2_title || ""
                this.group2Items = indicator.group_2_items || []
                this.group2Total = indicator.group_2_total
                this.isValid = {}
            }
            this.value = this.loadInitialValue(indicatorResults?.value ?? null)
            if (this.placeholder == null) {
                this.placeholder = this.loadInitialValue(null)
            }
            this.indicatorsStore.shallowIndicatorResultUpdate(this.code, this.value, this.notApplicable)
            this.required = indicator.required
            if (indicator.is_direct_indicator) {
                this.condition = indicator.condition
                this.validation = indicator.validation
            } else {
                this.formula = indicator.formula
            }
            this.msg = indicator.message
            this.show = (indicator.is_direct_indicator || indicator.display_indirect) && (indicator.condition == "" || this.indicatorsStore.isVisible(indicator))
            this.notApplicable = (indicatorResults?.not_applicable || !this.show) ?? false
            const field = {
                id: this.id,
                code: this.code,
                value: this.value,
                validation: this.validation,
                notApplicable: this.notApplicable,
                isValid: this.isValid,
                isGroupIndicator: this.isGroupIndicator,
            }
            const { isValid, isFieldValid } = this.indicatorsStore.validateField(field)
            this.isValid = isValid
        },
        loadInitialValue(initialValue) {
            let value = ""
            if (initialValue == null && this.indicatorsStore.isMultiAnswer(this.type)) {
                value = []
            }
            if (this.indicatorsStore.hasOptions(this.type)) {
                if (this.indicatorsStore.isMultiAnswer(this.type)) {
                    if (initialValue == "" || initialValue == null) {
                        value = []
                        this.options.forEach(o => this.checkedOptions.push(false))
                    } else {
                        optionIds = initialValue.split("|")
                        value = optionIds.map(id => this.getOption(id))
                        this.options.forEach(o => this.checkedOptions.push(optionIds.includes(o.id)))
                    }
                } else {
                    value = this.getOption(initialValue)
                }
            } else if (this.indicatorsStore.isGendered(this.type)) {
                if (initialValue && initialValue.female) {
                    value = {
                        female: initialValue.female,
                        male: initialValue.male,
                        nonBinary: initialValue.non_binary,
                    }
                } else {
                    // Do not set initial values to display the placeholder
                    value = {
                        female: null,
                        male: null,
                        nonBinary: null,
                    }
                }
            } else if (this.isGroupIndicator) {
                if (this.group2Title == "") {
                    value = this.loadListInitialValue(initialValue)
                } else {
                    value = this.loadTableInitialValue(initialValue)
                }
            } else if (initialValue != null) {
                value = initialValue
            }
            return value
        },
        loadListInitialValue(initialValue) {
            value = {}
            if (initialValue && Object.keys(initialValue).length > 0) {
                this.groupItems.forEach(item => {
                    value[item.suffix] = initialValue[item.suffix]
                    if (this.indicatorsStore.isNumeric(this.type)) {
                        value['total'] = this.groupItems.reduce((acc, curr) => acc + Number(value[curr.suffix]), 0)
                    }
                })
            } else {
                this.groupItems.forEach(item => {
                    value[item.suffix] = null
                })
            }
            return value
        },
        loadTableInitialValue(initialValue) {
            value = {}
            if (initialValue && Object.keys(initialValue).length > 0) {
                this.groupItems.forEach(item => {
                    value[item.suffix] = {}
                    this.group2Items.forEach(group2Item => {
                        value[item.suffix][group2Item.suffix] = initialValue[item.suffix][group2Item.suffix]
                    })
                    if (this.indicatorsStore.isNumeric(this.type)) {
                        value[item.suffix]['total'] = this.group2Items.reduce((acc, curr) => acc + Number(initialValue[item.suffix][curr.suffix] ?? 0), 0)
                    }
                })
                this.group2Items.forEach(group2Item => {
                    value[group2Item.suffix] = {}
                    value[group2Item.suffix]['total'] = this.groupItems.reduce((acc, curr) => acc + Number(initialValue[curr.suffix][group2Item.suffix] ?? 0), 0)
                })
                value['total'] = this.groupItems.reduce((acc, curr) => acc + Number(value[curr.suffix].total), 0)
            } else {
                this.groupItems.forEach(item => {
                    value[item.suffix] = {}
                    this.group2Items.forEach(group2Item => {
                        value[item.suffix][group2Item.suffix] = null
                    })
                    if (this.indicatorsStore.isNumeric(this.type)) {
                        value[item.suffix]['total'] = null
                    }
                })
                this.group2Items.forEach(group2Item => {
                    value[group2Item.suffix] = {}
                    value[group2Item.suffix]['total'] = null
                })
                value['total'] = null
            }
            return value
        },
        update(newValue, suffix = "", suffix2 = "") {
            try {
                this.value = this.updateValue(newValue, this.value, this.type, suffix, suffix2)
                const field = {
                    id: this.id,
                    code: suffix == "" ? this.code : suffix2 == "" ? `${this.code}_${suffix}` : `${this.code}_${suffix}_${suffix2}`,
                    value: this.value,
                    validation: this.validation,
                    notApplicable: this.notApplicable,
                    isValid: this.isValid,
                    isGroupIndicator: this.isGroupIndicator,
                }
                const { isValid, isFieldValid } = this.indicatorsStore.validateField(field, this.isGroupIndicator)
                this.isValid = isValid
                if (suffix == '') {
                    this.updateErrors(isFieldValid)
                } else if (suffix2 == '') {
                    this.updateErrors(isFieldValid || isValid[suffix])
                } else {
                    this.updateErrors(isFieldValid || isValid[suffix][suffix2])
                }
            } catch (e) {
                console.log('Invalido')
                console.log(e)
                this.hasErrors = true
                this.error = e.message
            }
        },
        updateValue(input, current, type, suffix = "", suffix2 = "") {
            // if (!current) return ""
            let value = ""
            if (this.indicatorsStore.hasOptions(type) && !this.indicatorsStore.isMultiAnswer(type)) {
                value = this.getOption(input)
            } else if (this.indicatorsStore.isMultiAnswer(type)) {
                //input is setted on the call to update from the x-effect of the component
                if (input && input.constructor == Array && input.length == 0 || input == "") {
                    value = []
                    this.checkedOptions = this.checkedOptions.map(o => false)
                } else {
                    const index = current.findIndex(v => v.id == input)
                    value = current
                    if (index != -1) {
                        value.splice(index, 1)
                        const optionIndex = this.options.findIndex(v => v.id == input)
                        this.checkedOptions[optionIndex] = false
                    } else {
                        value.push(this.getOption(input))
                        const optionIndex = this.options.findIndex(v => v.id == input)
                        this.checkedOptions[optionIndex] = true
                    }
                }
            } else if (this.isGroupIndicator || this.indicatorsStore.isGendered(type)) {
                value = current
                if (suffix2 == '') {
                    value[suffix] = input
                    if (this.indicatorsStore.isNumeric(type)) {
                        value['total'] = this.groupItems.reduce((acc, curr) => acc + Number(value[curr.suffix]), 0)
                    }
                } else {
                    value[suffix][suffix2] = input
                    if (this.indicatorsStore.isNumeric(this.type)) {
                        value[suffix]['total'] = this.group2Items.reduce((acc, curr) => acc + (Number(value[suffix][curr.suffix]) ?? 0), 0)
                        value[suffix2]['total'] = this.groupItems.reduce((acc, curr) => acc + (Number(value[curr.suffix][suffix2]) ?? 0), 0)
                        value['total'] = this.groupItems.reduce((acc, curr) => acc + (Number(value[curr.suffix].total || 0) ?? 0), 0)
                    }
                }
            } else {
                value = input
            }
            return value
        },
        updateNotApplicable(checked) {
            this.notApplicable = checked
            this.indicatorsStore.updateIndicatorResultNa(this.code, this.notApplicable)
            if (this.indicatorsStore.isMultiAnswer(this.type)) {
                this.update([])
            } else if (this.indicatorsStore.isGendered(this.type)) {
                this.update(0, "male")
                this.update(0, "female")
                this.update(0, "nonBinary")
            } else {
                this.update("")
            }
        },
        updateErrors(isFieldValid) {
            if (isFieldValid) {
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
        },
        isOptionSelected(optionId) {
            return this.value.id == optionId
        },
        getOption(id) {
            return this.options.find(o => o.id == id) || { value: "", id: "" }
        },
        setGroupItemValid(suffix, suffix2 = "") {
            if (suffix2 == "") {
                const el = document.querySelector(`#question_${this.id}_${suffix}`)
                el.classList.toggle('border-red-600', !this.isValid[suffix])
            } else {
                const el = document.querySelector(`#question_${this.id}_${suffix}_${suffix2}`)
                el.classList.toggle('border-red-600', !this.isValid[suffix][suffix2])
            }
        }
    }))
}

if (document.readyState === "complete" && Alpine) {
    initFieldData()
} else {
    document.addEventListener('alpine:init', initFieldData)
}