const initFieldData = () => {
    Alpine.data('field', (code = "", instanceNumber = -1) => ({
        id: "",
        instanceId: "",
        name: "",
        description: "",
        code: "",
        options: [],
        checkedOptions: [],
        placeholder: "",
        type: "",
        isDirectIndicator: true,
        displayIndirect: false,
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
        msg: "",
        unit: "",
        mandatory: false,
        state: {},
        indicatorsStore: Alpine.store('indicators'),
        init() {
            document.addEventListener('indicators-store:init', this.initIndicator(code, instanceNumber))
        },
        initIndicator(code, instanceNumber) {
            // Init field data
            const indicator = this.indicatorsStore.getIndicatorDataByCode(code)
            this.id = indicator.id
            this.instanceId = instanceNumber == -1 ? this.id : `${this.id}_${instanceNumber}`
            const indicatorResults = this.indicatorsStore["indicatorResults"][this.instanceId] || null
            this.placeholder = this.indicatorsStore["placeholders"][code] || null
            this.name = indicator.name
            this.description = indicator.description
            this.code = indicator.code
            this.type = indicator.data_type
            this.unit = indicator.unit
            this.mandatory = indicator.mandatory
            this.isDirectIndicator = indicator.is_direct_indicator
            this.displayIndirect = indicator.display_indirect
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
            }
            if (this.indicatorsStore.isGendered(this.type)) {
                this.groupItems = ['men', 'women', 'nonBinary']
                if (this.placeholder !== null) {
                    this.placeholder = {}
                    this.placeholder.women = this.indicatorsStore["placeholders"][code].female || null
                    this.placeholder.men = this.indicatorsStore["placeholders"][code].male || null
                    this.placeholder.nonBinary = this.indicatorsStore["placeholders"][code].non_binary || null
                }
            }
            const value = this.loadInitialValue(indicatorResults?.value ?? null)
            if (this.placeholder == null) {
                this.placeholder = this.loadInitialValue(null)
            }
            this.required = indicator.required
            this.condition = indicator.condition
            this.validation = indicator.validation
            if (!indicator.is_direct_indicator) {
                this.formula = indicator.formula
            }
            this.msg = indicator.message
            const show = (indicator.is_direct_indicator || indicator.display_indirect) && (indicator.condition == "" || this.indicatorsStore.isVisible(this.instanceId, indicator.condition))
            const notApplicable = (indicatorResults?.not_applicable || !show) ?? false

            // Init field state in store
            this.indicatorsStore['indicators'][this.instanceId] = {
                code,
                value: value,
                show,
                notApplicable: notApplicable,
                isValid: false,
                isFieldValid: false,
                hasErrors: false,
                error: ''
            }
            this.state = this.indicatorsStore['indicators'][this.instanceId]
            this.$dispatch('indicator-visible', { id: this.id, show })
            const { isValid, isFieldValid } = this.indicatorsStore.validateField(this.instanceId)
            this.state.isValid = isValid
            this.state.isFieldValid = isFieldValid
            this.$dispatch('indicator-valid', { id: this.id, isValid: isFieldValid })
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
                        women: initialValue.female,
                        men: initialValue.male,
                        nonBinary: initialValue.non_binary,
                    }
                } else {
                    // Do not set initial values to display the placeholder
                    value = {
                        women: null,
                        men: null,
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
                        value['total'] = this.groupItems.reduce((acc, curr) => acc + (Number(value[curr.suffix]) || 0), 0)
                        if (this.type == this.indicatorsStore.fieldTypes.DECIMAL) {
                            value['total'] = (Math.round(value['total'] * 100) / 100).toFixed(2)
                        }
                    }
                })
            } else {
                this.groupItems.forEach(item => {
                    value[item.suffix] = null
                })
                value['total'] = 0
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
                        if (this.type == this.indicatorsStore.fieldTypes.DECIMAL) {
                            value[item.suffix]['total'] = (Math.round(value[item.suffix]['total'] * 100) / 100).toFixed(2)
                        }
                    }
                })
                this.group2Items.forEach(group2Item => {
                    value[group2Item.suffix] = {}
                    value[group2Item.suffix]['total'] = this.groupItems.reduce((acc, curr) => acc + Number(initialValue[curr.suffix][group2Item.suffix] ?? 0), 0)
                    if (this.type == this.indicatorsStore.fieldTypes.DECIMAL) {
                        value[group2Item.suffix]['total'] = (Math.round(value[group2Item.suffix]['total'] * 100) / 100).toFixed(2)
                    }
                })
                value['total'] = this.groupItems.reduce((acc, curr) => acc + Number(value[curr.suffix].total), 0)
                if (this.type == this.indicatorsStore.fieldTypes.DECIMAL) {
                    value['total'] = (Math.round(value['total'] * 100) / 100).toFixed(2)
                }
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
        update(newValue, suffix = "", suffix2 = "", showErrors = true) {
            try {
                this.state = this.indicatorsStore['indicators'][this.instanceId]
                this.state.value = this.updateValue(newValue, this.state.value, this.type, suffix, suffix2)

                const { isValid, isFieldValid } = this.indicatorsStore.validateField(this.instanceId, suffix, suffix2, this.isGroupIndicator)
                this.state.isValid = isValid
                this.state.isFieldValid = isFieldValid
                if (showErrors) {
                    if (suffix == '') {
                        this.updateErrors(isFieldValid)
                    } else if (suffix2 == '') {
                        this.updateErrors(isFieldValid || isValid[suffix])
                    } else {
                        this.updateErrors(isFieldValid || isValid[suffix][suffix2])
                    }
                }
                this.$dispatch('indicator-valid', { id: this.id, isValid: isFieldValid })
            } catch (e) {
                console.log('Invalido')
                console.log(e)
                this.state.hasErrors = true
                this.state.error = e.message
            }
        },
        updateValue(input, current, type, suffix = "", suffix2 = "") {
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
                if (suffix2 == '' && suffix != '') {
                    value[suffix] = input
                    if (this.indicatorsStore.isNumeric(type)) {
                        value['total'] = this.groupItems.reduce((acc, curr) => acc + (Number(value[curr.suffix]) || 0), 0)
                        if (type == this.indicatorsStore.fieldTypes.DECIMAL) {
                            value['total'] = (Math.round(value['total'] * 100) / 100).toFixed(2)
                        }
                    }
                } else if (suffix2 != '' && suffix != '') {
                    value[suffix][suffix2] = input
                    if (this.indicatorsStore.isNumeric(this.type)) {
                        value[suffix]['total'] = this.group2Items.reduce((acc, curr) => acc + (Number(value[suffix][curr.suffix] || 0) ?? 0), 0)
                        value[suffix2]['total'] = this.groupItems.reduce((acc, curr) => acc + (Number(value[curr.suffix][suffix2] || 0) ?? 0), 0)
                        value['total'] = this.groupItems.reduce((acc, curr) => acc + (Number(value[curr.suffix].total || 0) ?? 0), 0)
                        if (type == this.indicatorsStore.fieldTypes.DECIMAL) {
                            value[suffix]['total'] = (Math.round(value[suffix]['total'] * 100) / 100).toFixed(2)
                            value[suffix2]['total'] = (Math.round(value[suffix2]['total'] * 100) / 100).toFixed(2)
                            value['total'] = (Math.round(value['total'] * 100) / 100).toFixed(2)
                        }
                    }
                } else {
                    value = this.loadInitialValue(input)
                }
            } else {
                value = input
            }
            return value
        },
        updateNotApplicable(checked, hide = false, showErrors = true) {
            this.state.notApplicable = checked
            if (hide) {
                this.updateShow(!checked, "", "", showErrors)
            }
            if (checked) {
                if (this.indicatorsStore.isMultiAnswer(this.type)) {
                    this.update([], "", "", showErrors)
                } else if (this.indicatorsStore.isGendered(this.type)) {
                    this.update(0, "women", "", showErrors)
                    this.update(0, "men", "", showErrors)
                    this.update(0, "nonBinary", "", showErrors)
                } else {
                    this.update("", "", "", showErrors)
                }
            }
        },
        updateErrors(isFieldValid) {
            if (isFieldValid) {
                this.state.hasErrors = false
            } else {
                this.state.hasErrors = true
                if (this.msg) {
                    this.state.error = this.msg
                } else if (this.validation == "") {
                    this.state.error = gettext("Required field.")
                } else {
                    this.state.error = gettext('Value it\'s incorrect, has to meet condition: ') + this.validation;
                }
            }
            this.indicatorsStore.updateIndicatorDependencies(this.instanceId)

        },
        updateShow(show) {
            // Only if it has changed
            if (this.state.show != show) {
                if (this.isDirectIndicator) {
                    this.state.show = show
                    // Show direct indicator and unset NA
                    if (show) {
                        this.state.notApplicable = false
                    }
                    this.$dispatch('indicator-visible', { id: this.id, show })
                } else {
                    // Show/hide indirect indicator
                    if (this.displayIndirect) {
                        this.state.show = show
                        this.$dispatch('indicator-visible', { id: this.id, show })
                    }
                }
            }
        },
        isOptionSelected(optionId) {
            return this.state.value.id == optionId
        },
        getOption(id) {
            return this.options.find(o => o.id == id) || { value: null, id: "" }
        },
        copyFieldOptions(id) {
            const fieldEl = document.getElementById(`question_${id}`)
            this.options = Alpine.$data(fieldEl).options
            this.checkedOptions = Alpine.$data(fieldEl).checkedOptions
        },
        setGroupItemValid(suffix, suffix2 = "") {
            if (suffix2 == "") {
                const el = document.querySelector(`#question_${this.id}_${suffix}`)
                el.classList.toggle('border-red-600', !this.state.isValid[suffix])
            } else {
                const el = document.querySelector(`#question_${this.id}_${suffix}_${suffix2}`)
                el.classList.toggle('border-red-600', !this.state.isValid[suffix][suffix2])
            }
        },
        fillWithZeros() {
            if (this.groupItems.length > 0) {
                if (this.group2Items.length > 0) {
                    this.groupItems.forEach(i => {
                        this.group2Items.forEach(ii => {
                            if (this.state.value[i.suffix][ii.suffix] == null || this.state.value[i.suffix][ii.suffix] == "") {
                                this.update(0, i.suffix, ii.suffix)
                                this.setGroupItemValid(i.suffix, ii.suffix)
                            }
                        })
                    })
                } else {
                    this.groupItems.forEach(i => {
                        if (this.state.value[i.suffix] == null || this.state.value[i.suffix] == "") {
                            this.update(0, i.suffix)
                            this.setGroupItemValid(i.suffix)
                        }
                    })
                }
            }
        },
        validateGroup() {
            try {
                const { isValid, isFieldValid } = this.indicatorsStore.validateField(this.instanceId, '', '', false, true)
                this.state.isValid = isValid
                this.state.isFieldValid = isFieldValid
                this.updateErrors(isFieldValid)
                this.$dispatch('indicator-valid', { id: this.id, isValid: isFieldValid })
                if (isFieldValid) {
                    const btnEl = document.querySelector(`#field_${this.instanceId} .validate-group-btn `);
                    btnEl.style.transition = "all .4s ease"
                    btnEl.style.borderColor = "oklch(62.7% 0.194 149.214)" // green-600
                    btnEl.style.backgroundColor = "oklch(62.7% 0.194 149.214)" // green-600
                    setTimeout(() => {
                        btnEl.style.backgroundColor = "oklch(54.6% 0.245 262.881)" // blue-600
                        btnEl.style.borderColor = "oklch(54.6% 0.245 262.881)" // blue-600
                    }, 1000)
                }
            } catch (e) {
                console.log('Invalido')
                console.log(e)
                this.state.hasErrors = true
                this.state.error = e.message
            }
        }
    }))
}

if (document.readyState === "complete" && Alpine) {
    initFieldData()
} else {
    document.addEventListener('alpine:init', initFieldData)
}