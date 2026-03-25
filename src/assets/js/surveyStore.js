/* 
    Section state
    {
        show
        touched
        isValid
    }
*/

const initSurveyStore = () => {
    Alpine.store('survey', {
        sections: {},
        sectionsData: [],
        topSectionsData: [],
        currentSection: "",
        prevSection: "",
        prevSectionId: "",
        validatedSections: [],
        indicators: Alpine.store('indicators')['indicators'],
        indicatorsData: Alpine.store('indicators')['indicatorsData'],
        indicatorsStore: Alpine.store('indicators'),
        initSections(sections) {
            // Clear
            sections.forEach(s => this.sections[s.id] = {
                show: false,
                touched: false,
                isValid: false,
            })
            this.sectionsData = sections
            this.currentSection = ""
            this.prevSection = ""
            this.prevIdSection = ""
            this.validatedSections = []
            this.topSectionsData = sections.filter(s => s.parent_id == null)
            // Init
            setTimeout(() => {
                this.sections[this.sectionsData[0].id].touched = true
                this.currentSection = this.sectionsData[0].id
            }, 200)
        },
        setSection(id, triggerTab) {
            const index = this.topSectionsData.findIndex(s => s.id == id)
            if (index != null && index != -1) {
                this.currentSection = this.topSectionsData[index].id
                this.sections[id].touched = true
                if (index > 0) {
                    this.prevSection = this.topSectionsData[index - 1].title
                    this.prevSectionId = this.topSectionsData[index - 1].id
                } else {
                    this.prevSection = ""
                    this.prevSectionId = ""
                }
                if (triggerTab) {
                    FlowbiteInstances.getAllInstances().Tabs["survey-tabs"].show(`#section-${id}`)
                }
            } else {
                console.log("section doesn't exist", id)
            }
            window.scrollTo(0, 0)
        },
        gotToPrevSection() {
            const index = this.topSectionsData.findIndex(s => s.id == this.prevSectionId)
            this.setSection(this.topSectionsData[index].id, true)
        },
        goToField(code, sectionId) {
            // Change tab
            FlowbiteInstances.getAllInstances().Modal['survey-errors-modal'].hide()
            const section = this.sectionsData.find(s => s.id == sectionId)
            const topSectionId = section.parent_id == null ? sectionId : section.parent_id
            this.setSection(topSectionId, true)

            // Scroll to field
            const fieldEl = document.getElementById(`field-${this.indicatorsData.find(i => i.code == code).id}`)
            const headerOffset = 110
            const elementPosition = fieldEl.getBoundingClientRect().top
            const offsetPosition = elementPosition + window.scrollY - headerOffset
            window.scrollTo({ top: offsetPosition, behavior: "smooth" })
        },
        setInvalidIndicators() {
            let validatedSections = []
            this.sectionsData.forEach(s => {
                let invalidIndicators = []
                s.indicators_codes.forEach(code => {
                    if (!this.indicators[code].isFieldValid) {
                        const indicator = this.indicatorsData.find(i => i.code == code)
                        if (!!indicator) {
                            invalidIndicators.push({
                                code: code,
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
            for (let i = 0; i < this.sectionsData.length; i++) {
                let s = this.sectionsData[i]
                const index = s.indicators_codes.findIndex(code => this.indicators[code].isFieldValid == false)

                if (index > -1) {
                    this.setInvalidIndicators()
                    let showModalEvent = new Event('show-modal')
                    showModalEvent.detail = { 'id': 'survey-errors-modal' }
                    window.dispatchEvent(showModalEvent)
                    isValid = false
                    break
                }
            }
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