document.addEventListener('alpine:init', () => {
    // reference: https://codepen.io/KevinBatdorf/pen/QWyQqZb
    Alpine.store('notifications', {
        notifications: [],
        visible: [],
        add(notification) {
            notification.id = Date.now()
            notification.animationTime = this.getAnimationTime()
            this.notifications.push(notification)
            this.fire(notification)
        },
        fire(notification) {
            this.visible.push(notification)
            setTimeout(() => {
                this.remove(notification.id)
            }, notification.animationTime)
        },
        remove(id) {
            console.log(this.visible)
            const notification = this.visible.find(notification => notification.id == id)
            const index = this.visible.indexOf(notification)
            this.visible.splice(index, 1)
        },
        getAnimationTime() {
            const delta = 1
            const transitionTime = 800
            return (7000 * delta) - (transitionTime * delta)
        },
        getBgColor(type, shade) {
            return `bg-${this.getThemeColor(type)}-${shade}`
        },
        getThemeColor(type) {
            switch (type) {
                case 'success': return 'green'
                case 'warning': return 'orange'
                case 'error': return 'red'
                default: return 'blue'
            }
        },
    })
})