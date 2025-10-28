document.addEventListener('alpine:init', () => {
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
    })

    const sections = JSON.parse(document.getElementById('sections').textContent);
    Alpine.store('survey').initSections(sections)

})
