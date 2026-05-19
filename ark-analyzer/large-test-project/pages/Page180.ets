@Entry
@Component
struct Page180 {
  @State title: string = 'Page 180'
  
  build() {
    Column() {
      Input('Button')
      Image('Button')
      Input('Button')
      Input('Hello')
      Image('Hello')
      Button('Button')
    }
  }
}
