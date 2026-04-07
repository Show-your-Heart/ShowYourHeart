const initFielsSetdData = () => {
    Alpine.data('fieldsSet', (opts = { code: '', name: '' }) => ({
        id: "",
        code: "",
        name: "",
        title: "",
        description: "",
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
            const firstIndicatorId = indicatorsSet.indicators_ids[0]

            // Init set instances
            const indicatorResults = this.indicatorsStore["indicatorResults"]
            Object.keys(indicatorResults).forEach(instanceId => {
                let id = instanceId.split("_")[0]
                let instanceNumber = instanceId.split("_")[1]
                if (id == firstIndicatorId && instanceNumber > this.idsCounter) {
                    this.idsCounter = instanceNumber
                }
                if (instanceNumber !== undefined && !this.instances.includes(Number(instanceNumber))) {
                    this.instances.push(Number(instanceNumber))
                    this.totalInstances++
                }
            })
            setTimeout(() => {
                this.initAccordion()
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
        }

    }))
}

if (document.readyState === "complete" && Alpine) {
    initFielsSetdData()
} else {
    document.addEventListener('alpine:init', initFielsSetdData)
}