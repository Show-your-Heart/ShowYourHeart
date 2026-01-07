const initSurveyStore = () => {
    Alpine.store('survey', {
        sections: [],
        currentSection: "",
        prevSection: "",
        prevSectionId: "",
        initSections(sections) {
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
        setSection(title) {
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
        onSumbit(e) {
            if (e.submitter.value === "submit") {
                //check isValid. if not valid, the value remains empty
                this.sections.forEach(s => {
                    const index = s.indicatorsStats.findIndex(i => i.isValid == false)
                    if (index > -1) {
                        e.preventDefault()
                    }
                })

                const methodIndicators = Alpine.store('indicators')["indicators"]
                const mandatoryIndicators = methodIndicators.filter(i => i.mandatory && !i.not_applicable)
                let emptyMandatoryQuestions = []
                mandatoryIndicators.forEach(mi => {
                    // Works for object values (gendered questions) and arrays (multi answer questions)
                    if (mi.value != null && typeof (mi.value) == 'object') {
                        const isEmpty = Object.values(mi.value).every(x => x === null || x === '');
                        if (isEmpty) {
                            emptyMandatoryQuestions.push(mi)
                        }
                    }
                })

                if (emptyMandatoryQuestions.length) {
                    e.preventDefault()
                    console.log("not mandatory questions empty", emptyMandatoryQuestions)
                }

            }
        },
    })

    if(document.getElementById('sections')){
        const sections = JSON.parse(document.getElementById('sections').textContent);
        Alpine.store('survey').initSections(sections)
    }
}

if(document.readyState === "complete" && Alpine){
    initSurveyStore()
} else {
    document.addEventListener('alpine:init', initSurveyStore)
}