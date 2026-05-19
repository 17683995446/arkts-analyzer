@Entry
@Component
struct Index {
  @State message: string = 'Hello World'

  build() {
    Column() {
      Text(this.message)
        .fontSize(50)
        .fontWeight(FontWeight.Bold)

      Button('Click me')
        .onClick(() => {
          this.message = 'Welcome to ArkAnalyzer!'
        })
    }
    .width('100%')
    .height('100%')
  }
}

export default Index
