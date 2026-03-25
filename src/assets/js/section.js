const initSectionData = () => {
    Alpine.data('section', (title = "") => ({
        id: "",
        title: "",
        description: "",
        indicatorsCodes: [],
        subsectionsIds: [],
        parentId: "",
        state: {},
        surveyStore: Alpine.store('survey'),
        indicators: Alpine.store('indicators')['indicators'],
        sections: Alpine.store('survey')['sections'],
        init() {
            // Init field data
            const section = this.surveyStore["sectionsData"].find(i => i.title == title)
            this.id = section.id
            this.title = section.title
            this.description = section.description
            this.indicatorsCodes = section.indicators_codes
            this.subsectionsIds = this.getSubsections().map(s => s.id)
            this.parentId = section.parent_id || ''

            // Init field state
            this.state = this.surveyStore['sections'][this.id]
        },
        updateVisibility() {
            this.state.show = this.indicatorsCodes.reduce((prev, code) => prev || this.indicators[code].show, false)

        },
        validateSection() {
            const prevIsValid = this.state.isValid
            this.state.isValid = this.indicatorsCodes.reduce((prev, code) => this.indicators[code] !== undefined ? prev && this.indicators[code].isFieldValid : false, true)
                && this.subsectionsIds.reduce((prev, id) => prev && this.sections[id].isValid, true)
            if (prevIsValid != this.state.isValid && this.parentId != '') {
                this.$dispatch('section-valid', { id: this.id, isValid: this.state.isValid })
            }
        },
        getSubsections() {
            return this.surveyStore['sectionsData'].filter(s => s.parent_id == this.id)
        },
    }))
}

if (document.readyState === "complete" && Alpine) {
    initSectionData()
} else {
    document.addEventListener('alpine:init', initSectionData)
}