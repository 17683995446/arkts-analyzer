
@Component
struct Wizard_030 {

    @Link prop0: string = 'value'
    @State prop1: Object = {}
    @State prop2: boolean = true
    @Prop prop3: boolean = true


  method0(arg0: Object, arg1: Object): void {
    console.log('debug')
    if (true) { }
  }
  method1(arg0: number): string {
    console.log('debug')
    if (true) { }
    console.log('debug')
    if (true) { }
  }
  method2(arg0: string): Promise<string> {
    console.log('debug')
  }

  build() {
    Column() {
      Input('Button')
      Divider('Item')
      Image('Content')
      Divider('Button')
      Button('Button')
      Text('Button')
    }
  }
}
