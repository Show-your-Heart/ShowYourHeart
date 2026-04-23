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
        goToField(instanceId, sectionId) {
            // Change tab
            FlowbiteInstances.getAllInstances().Modal['survey-errors-modal'].hide()
            const section = this.sectionsData.find(s => s.id == sectionId)
            const topSectionId = section.parent_id == null ? sectionId : section.parent_id
            this.setSection(topSectionId, true)

            // If set element open it
            if (instanceId.split("_").length == 2) {
                const headingEl = document.getElementById(`field_${instanceId}`).parentNode.previousElementSibling
                if (headingEl.getAttribute('aria-expanded') === 'false') {
                    headingEl.click()
                }
            }

            // Scroll to field
            const fieldEl = document.getElementById(`field_${instanceId}`)
            const headerOffset = 110
            const elementPosition = fieldEl.getBoundingClientRect().top
            const offsetPosition = elementPosition + window.scrollY - headerOffset
            window.scrollTo({ top: offsetPosition, behavior: "smooth" })
        },
        setInvalidIndicators() {
            let hasInvalidIndicators = false
            let validatedSections = []
            let indicatorsInSets = []
            this.indicatorsStore["indicatorsSets"].forEach(s => indicatorsInSets = [...indicatorsInSets, ...s.indicators_ids])

            this.sectionsData.forEach(s => {
                let invalidIndicators = []
                s.indicators_ids.forEach(id => {
                    // Validate regular fields
                    if (!this.indicators[id].isFieldValid) {
                        const indicator = this.indicatorsStore.getIndicatorDataById(id)
                        if (!!indicator) {
                            hasInvalidIndicators = true
                            invalidIndicators.push({
                                code: indicator.code,
                                instanceId: indicator.id,
                                name: indicator.name
                            })
                        }
                    }
                })
                // Validate section setcs
                s.indicators_sets_ids.forEach(sectionId => {
                    const indicatorsSet = this.indicatorsStore["indicatorsSets"].find(s => s.id == sectionId)
                    const keys = Object.keys(this.indicators)
                    indicatorsSet.indicators_ids.forEach(id => {
                        const instancesIds = keys.filter(k => k.includes(id))
                        instancesIds.forEach(instanceId => {
                            if (!this.indicators[instanceId].isFieldValid) {
                                const indicator = this.indicatorsStore.getIndicatorDataById(id)
                                if (!!indicator) {
                                    hasInvalidIndicators = true
                                    invalidIndicators.push({
                                        code: `${indicator.code} - #${instanceId.split('_')[1]}`,
                                        instanceId: instanceId,
                                        name: indicator.name
                                    })
                                }
                            }
                        })
                    })
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
            return hasInvalidIndicators
        },
        validateSurvey() {
            let isValid = true

            // Check all fields are valid.
            const hasInvalidIndicators = this.setInvalidIndicators()
            if (hasInvalidIndicators) {
                let showModalEvent = new Event('show-modal')
                showModalEvent.detail = { 'id': 'survey-errors-modal' }
                window.dispatchEvent(showModalEvent)
                isValid = false
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