@Component
@Entry
struct Grid_142 {
  @State title: string = 'Component 142'
  @State count: number = 0
  @State isActive: boolean = false
  
  build() {
    Column() {
      Text(this.title)
        .fontSize(24)
        .fontWeight(FontWeight.Bold)
      
      Button('Click Me')
        .onClick(() => {
          this.count++
          this.isActive = !this.isActive
        })
      
      Text(`Count: ${this.count}`)
        .fontSize(18)
        .margin({ top: 20 })
      
      if (this.isActive) {
        Text('Component is active!')
          .fontColor(Color.Green)
          .margin({ top: 10 })
      }
    }
    .width('100%')
    .padding(20)
  }
  
  private increment() {
    this.count++
  }
  
  private reset() {
    this.count = 0
  }
}
