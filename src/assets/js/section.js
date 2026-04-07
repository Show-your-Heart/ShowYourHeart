const initSectionData = () => {
    Alpine.data('section', (title = "") => ({
        id: "",
        title: "",
        description: "",
        indicatorsIds: [],
        indicatorsSetsIds: [],
        indicatorsInstanceIds: [],
        subsectionsIds: [],
        parentId: "",
        state: {},
        surveyStore: Alpine.store('survey'),
        indicators: Alpine.store('indicators')['indicators'],
        sections: Alpine.store('survey')['sections'],
        init() {
            // Init section data
            const section = this.surveyStore["sectionsData"].find(i => i.title == title)
            this.id = section.id
            this.title = section.title
            this.description = section.description
            this.indicatorsIds = section.indicators_ids
            this.indicatorsSetsIds = section.indicators_sets_ids
            // Track fields and sets instances for validation and visibility
            this.setIndicatorsInstanceIds()
            this.subsectionsIds = this.getSubsections().map(s => s.id)
            this.parentId = section.parent_id || ''

            // Init field state
            this.state = this.surveyStore['sections'][this.id]
        },
        updateVisibility() {
            this.state.show = this.indicatorsInstanceIds.reduce((prev, instanceId) => prev || this.indicators[instanceId].show, false)
        },
        validateSection() {
            const prevIsValid = this.state.isValid
            this.state.isValid = this.indicatorsInstanceIds.reduce((prev, instanceId) => this.indicators[instanceId] !== undefined ? prev && this.indicators[instanceId].isFieldValid : false, true)
                && this.subsectionsIds.reduce((prev, id) => prev && this.sections[id].isValid, true)
            if (prevIsValid != this.state.isValid && this.parentId != '') {
                this.$dispatch('section-valid', { id: this.id, isValid: this.state.isValid })
            }
        },
        getSubsections() {
            return this.surveyStore['sectionsData'].filter(s => s.parent_id == this.id)
        },
        setIndicatorsInstanceIds() {
            const instanceIds = Object.keys(Alpine.store('indicators')['indicatorResults'])
            if (instanceIds.length > 0) {
                this.indicatorsIds.forEach(id => {
                    const instanceId = instanceIds.find(k => k.includes(id))
                    if (!!instanceId && !this.indicatorsInstanceIds.includes(instanceId)) {
                        this.indicatorsInstanceIds.push(instanceId)
                    }
                })
                this.indicatorsSetsIds.forEach(sectionId => {
                    const indicatorsSet = Alpine.store('indicators')["indicatorsSets"].find(s => s.id == sectionId)
                    indicatorsSet.indicators_ids.forEach(id => {
                        const setInstanceIds = instanceIds.filter(k => k.includes(id))
                        setInstanceIds.forEach(instanceId => {
                            if (!!instanceId && !this.indicatorsInstanceIds.includes(instanceId)) {
                                this.indicatorsInstanceIds.push(instanceId)
                            }
                        })
                    })
                })
            } else {
                this.indicatorsInstanceIds = this.indicatorsIds
                this.indicatorsSetsIds.forEach(setId => {
                    const indicatorsSet = Alpine.store('indicators')["indicatorsSets"].find(s => s.id == setId)
                    indicatorsSet.indicators_ids.forEach(id => {
                        this.indicatorsInstanceIds.push(`${id}_1`)
                    })
                })
            }
        },
        addInstanceIds(setId, instanceNumber) {
            const indicatorsSet = Alpine.store('indicators')["indicatorsSets"].find(s => s.id == setId)
            indicatorsSet.indicators_ids.forEach(id => {
                this.indicatorsInstanceIds.push(`${id}_${instanceNumber}`)
            })
        },
        removeInstanceIds(setId, instanceNumber) {
            const indicatorsSet = Alpine.store('indicators')["indicatorsSets"].find(s => s.id == setId)
            indicatorsSet.indicators_ids.forEach(id => {
                const index = this.indicatorsInstanceIds.findIndex(i => i == `${id}_${instanceNumber}`)
                if (index != -1) {
                    this.indicatorsInstanceIds.splice(index, 1)
                }
            })
        }
    }))
}

if (document.readyState === "complete" && Alpine) {
    initSectionData()
} else {
    document.addEventListener('alpine:init', initSectionData)
}