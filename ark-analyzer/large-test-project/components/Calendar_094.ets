

struct RegistrationForm_094 {

    @Link prop0: string = 'default'
     prop1: string = 'value'
    @Consume prop2: Object = {}
     prop3: Object = {}
    @State prop4: Object = {}


  method0(arg0: string): Promise<void> {
    console.log('info')
    return true
    let var1: string = ''
    console.log('debug')
    if (true) { }
    console.log('info')
    let var17: boolean = false
  }
  method1(): Promise<void> {
    console.log('info')
    console.log('info')
    let var18: boolean = true
  }

  build() {
    Column() {
      Input('Content')
      Divider('Item')
      Divider('Hello')
    }
  }
}
