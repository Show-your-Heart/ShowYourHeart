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
            console.log("------------------------------------------------------------")
            console.log(" Init section --> ", section.title)

            this.id = section.id
            this.title = section.title
            this.description = section.description
            this.indicatorsCodes = section.indicators_codes
            this.subsectionsIds = this.getSubsections().map(s => s.id)
            this.parentId = section.parent_id || ''

            // Init field state
            this.state = this.surveyStore['sections'][this.id]
            // TODO: init section visibility after all fields are initialized
            // setTimeout(() => {
            //     this.updateVisibility()
            //     this.validateSection()
            // }, 1000)
        },
        updateVisibility() {
            this.state.show = this.indicatorsCodes.reduce((prev, code) => prev || this.indicators[code].show, false)
            // console.log("check visibility section", this.title, this.state.show)

        },
        validateSection() {
            const prevIsValid = this.state.isValid
            this.state.isValid = this.indicatorsCodes.reduce((prev, code) => prev && this.indicators[code].isFieldValid, true)
                && this.subsectionsIds.reduce((prev, id) => prev && this.sections[id].isValid, true)
            if (prevIsValid != this.state.isValid && this.parentId != '') {
                // console.log("dispatch validation event", this.title, this.state.isValid)
                this.$dispatch('section-valid', { id: this.id, isValid: this.state.isValid })
                // } else if (prevIsValid != this.state.isValid && this.parentId == '') {
                //     this.surveyStore.updateSectionValidation(this.id, this.state.isValid)
            }
            console.log(
                ".o.o.o. validate section",
                // this.title,
                this.state.isValid,
                this.indicatorsCodes.map(code => this.indicators[code].isFieldValid),
                this.subsectionsIds.map(id => this.sections[id].isValid)
            )


            // console.log(this.indicatorsValidation, !!(this.indicatorsValidation.reduce((prev, curr) => prev && curr, true)))

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