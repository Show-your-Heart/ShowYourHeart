const initSurveyStore = () => {
    Alpine.store('survey', {
        sections: [],
        currentSection: "",
        prevSection: "",
        prevSectionId: "",
        validatedSections: [],
        initSections(sections) {
            // Clear
            this.sections = []
            this.currentSection = ""
            this.prevSection = ""
            this.prevIdSection = ""
            this.validatedSections = []
            // Init
            sections.forEach(s =>
                this.sections.push({
                    id: s.id,
                    title: s.title,
                    indicatorsStats: s.indicators_ids.map(i => ({ id: i, isValid: false })),
                    touched: false,
                })
            );
            this.sections[0].touched = true
            this.currentSection = this.sections[0].title
        },
        setSection(title, triggerTab) {
            const index = this.sections.findIndex(s => s.title == title)
            if (index != null && index != -1) {
                this.currentSection = this.sections[index].title
                this.sections[index].touched = true
                if (index > 0) {
                    this.prevSection = this.sections[index - 1].title
                    this.prevSectionId = this.sections[index - 1].id
                } else {
                    this.prevSection = ""
                    this.prevSectionId = ""
                }
                if (triggerTab) {
                    FlowbiteInstances.getAllInstances().Tabs["survey-tabs"].show(`#section-${this.sections[index].id}`)
                }
            } else {
                console.log("section doesn't exist", title)
            }
        },
        gotToPrevSection() {
            const index = this.sections.findIndex(s => s.id == this.prevSectionId)
            this.prevSection = this.sections[index].title
            if (index == 0) {
                this.prevSectionId = ""
                this.prevSection = ""
            } else {
                this.prevSectionId = this.sections[index - 1].id
            }
            FlowbiteInstances.getAllInstances().Tabs["survey-tabs"].show(`#section-${this.sections[index].id}`)
        },
        isSectionCompleted(title) {
            const section = this.sections.find(s => s.title == title)
            if (section) {
                return section.indicatorsStats.reduce((acc, curr) => acc && curr.isValid, true)
            }
            return false
        },
        isSectionTouched(title) {
            const section = this.sections.find(s => s.title == title)
            if (section) {
                return section.touched
            } else {
                console.log("section doesn't exist", title)
            }
            return false
        },
        setIndicatorValidation(id, value) {
            this.sections.forEach(s => {
                const index = s.indicatorsStats.findIndex(i => i.id == id)
                if (index > -1) {
                    s.indicatorsStats[index].isValid = value
                }
            })
        },
        getInvalidIndicatos() {
            let validatedSections = []
            this.sections.forEach(s => {
                let invalidIndicators = []
                s.indicatorsStats.forEach(i => {
                    if (!i.isValid) {
                        const indicator = Alpine.store('indicators')['indicators'].find(ind => i.id == ind.id)
                        if (!!indicator) {
                            const fieldEl = document.querySelector(`#field-${indicator.id}`);
                            const fieldData = Alpine.$data(fieldEl)
                            const { isValid, isFieldValid } = Alpine.store('indicators').validateField({
                                id: fieldData.id,
                                code: fieldData.code,
                                value: fieldData.value,
                                validation: fieldData.validation,
                                isValid: fieldData.isValid,
                                notApplicable: fieldData.notApplicable,
                            }, false, true)
                            Alpine.$data(fieldEl).updateErrors(isFieldValid)
                            invalidIndicators.push({
                                code: indicator.code,
                                name: indicator.name
                            })
                        }
                    }
                })
                if (invalidIndicators.length > 0) {
                    validatedSections.push({
                        id: s.id,
                        title: s.title,
                        invalidIndicators
                    })
                }
            })
            this.validatedSections = validatedSections
        },
        validateSurvey() {
            let isValid = true
            //check isValid. if not valid, the value remains empty
            this.sections.forEach(s => {
                const index = s.indicatorsStats.findIndex(i => i.isValid == false)
                if (index > -1) {
                    this.getInvalidIndicatos()
                    let showModalEvent = new Event('show-modal')
                    showModalEvent.detail = { 'id': 'survey-errors-modal' }
                    window.dispatchEvent(showModalEvent)
                    isValid = false
                }
            })
            return isValid
        },
        onSubmit(e) {
            if (e.target.value === "submit") {
                if (!this.validateSurvey()) {
                    e.preventDefault()
                }
            }
        },
    })

    if (document.getElementById('sections')) {
        const sections = JSON.parse(document.getElementById('sections').textContent);
        Alpine.store('survey').initSections(sections)
    }
}

if (document.readyState === "complete" && Alpine) {
    initSurveyStore()
} else {
    document.addEventListener('alpine:init', initSurveyStore)
}