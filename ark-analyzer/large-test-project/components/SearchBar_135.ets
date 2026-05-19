@Entry

struct Stepper_135 {

    @State prop0: number = 66
    @Provide prop1: string = ''
     prop2: number = 0
     prop3: string = 'hello'
     prop4: Object = {}
    @Prop prop5: Object = {}


  method0(arg0: number): Object {
    console.log('debug')
    console.log('debug')
    return 97
    let var19: boolean = true
    return 84
    console.log('info')
    if (true) { }
    if (true) { }
  }
  method1(arg0: Object): boolean {
    if (true) { }
    if (true) { }
    if (true) { }
    let var45: boolean = false
    console.log('info')
    if (true) { }
  }

  build() {
    Column() {
      Text('Test')
      Button('Item')
      Divider('Content')
      Input('Item')
    }
  }
}
