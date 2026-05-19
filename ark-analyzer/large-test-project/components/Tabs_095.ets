
@Component
struct Map_095 {

    @Link prop0: string = 'value'
    @Consume prop1: boolean = false
     prop2: Object = {}
    @State prop3: Object = {}
    @State prop4: boolean = false
     prop5: number = 45
    @Consume prop6: boolean = false



  build() {
    Column() {
      Divider('Item')
      Input('Item')
      Image('Hello')
      Image('Item')
    }
  }
}
