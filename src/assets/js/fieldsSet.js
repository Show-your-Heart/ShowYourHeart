const initFielsSetdData = () => {
    Alpine.data('fieldsSet', (opts = { code: '', name: '' }) => ({
        id: "",
        code: "",
        name: "",
        title: "",
        description: "",
        condition: "",
        show: true,
        indicatorsIds: [],
        totalInstances: 1,
        idsCounter: 1,
        instances: [1],
        indicatorsStore: Alpine.store('indicators'),
        init() {
            this.code = opts.code
            this.name = opts.name
            const indicatorsSet = this.indicatorsStore["indicatorsSets"].find(i => i.code == this.code)
            this.id = indicatorsSet.id
            this.title = indicatorsSet.name
            this.description = indicatorsSet.description
            this.indicatorsIds = indicatorsSet.indicators_ids
            const firstIndicatorId = indicatorsSet.indicators_ids[0]
            this.show = indicatorsSet.condition != "" ? this.indicatorsStore.isVisible("", indicatorsSet.condition) : true

            // Init set instances
            const indicatorResults = this.indicatorsStore["indicatorResults"]
            Object.keys(indicatorResults).forEach(instanceId => {
                let id = instanceId.split("_")[0]
                let instanceNumber = instanceId.split("_")[1]
                if (id == firstIndicatorId && instanceNumber > this.idsCounter) {
                    this.idsCounter = instanceNumber
                }
                if (instanceNumber !== undefined && !this.instances.includes(Number(instanceNumber)) && this.indicatorsIds.includes(id)) {
                    this.instances.push(Number(instanceNumber))
                    this.totalInstances++
                }
            })
            setTimeout(() => {
                this.initAccordion()
                if (!this.show) {
                    this.updateSetIndicatorsShow(this.show)
                }
            }, 100)
        },
        add() {
            this.idsCounter++
            this.instances.push(this.idsCounter)
            this.totalInstances++

            this.refreshAccordion()
            this.$dispatch('add-instance', { setId: this.id, instanceNumber: this.idsCounter })
        },
        remove(instanceId) {
            this.instances.splice(this.instances.findIndex(i => i == instanceId), 1)
            this.totalInstances--
            this.refreshAccordion(false)
            this.$dispatch('remove-instance', { setId: this.id, instanceNumber: instanceId })
        },
        refreshAccordion(collapse = true) {
            const accordion = FlowbiteInstances.getInstance('Accordion', `set_${this.code}`)
            accordion.removeInstance()
            setTimeout(() => {
                this.initAccordion(collapse)
            }, 100)
        },
        initAccordion(collapse = true) {
            const items = this.instances.map(i => ({
                id: `${this.name}-heading-${i}`,
                triggerEl: document.querySelector(`#${this.name}-heading-${i}`),
                targetEl: document.querySelector(`#${this.name}-body-${i}`),
                active: false
            }))
            const accordion = new Accordion(document.getElementById(`set_${this.code}`), items)
            if (collapse) {
                accordion.open(`${this.name}-heading-${this.instances[this.instances.length - 1]}`)
            }
        },
        updateShow(show) {
            // Only if it has changed
            if (this.show != show) {
                this.show = show
                this.updateSetIndicatorsShow(show)
            }
        },
        updateSetIndicatorsShow(show) {
            this.instances.forEach(instanceNumber => {
                this.indicatorsIds.forEach(id => {
                    const instanceId = `${id}_${instanceNumber}`
                    const fieldEl = document.querySelector(`#field_${instanceId}`);
                    const showField = show
                    Alpine.$data(fieldEl).updateShow(showField)

                    this.indicatorsStore.updateIndicatorResultNa(instanceId, !show, !show)

                    // Update validation
                    const { isValid, isFieldValid } = this.indicatorsStore.validateField(instanceId)
                    this.indicatorsStore.indicators[instanceId].isValid = isValid
                    this.indicatorsStore.indicators[instanceId].isFieldValid = isFieldValid
                    Alpine.$data(fieldEl).$dispatch('indicator-valid', { id, isValid: isFieldValid })
                })
            })
        }
    }))
}

if (document.readyState === "complete" && Alpine) {
    initFielsSetdData()
} else {
    document.addEventListener('alpine:init', initFielsSetdData)
}