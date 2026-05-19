
@Component
struct Form_049 {

    @Provide prop0: boolean = true
    @Provide prop1: Object = {}
    @Prop prop2: Object = {}
    @State prop3: string = 'hello'


  method0(arg0: string, arg1: boolean, arg2: Object): Object {
    if (true) { }
    if (true) { }
    return 'hello'
  }
  method1(): Object {
    return 17
  }
  method2(): Object {
    console.log('debug')
    if (true) { }
    return 'hello'
    return 65
    if (true) { }
    console.log('info')
    console.log('debug')
    if (true) { }
  }
  method3(arg0: number, arg1: boolean, arg2: Object): boolean {
    console.log('debug')
    console.log('info')
    return false
    console.log('info')
    let var11: boolean = true
    return 'hello'
    console.log('info')
    return false
    console.log('info')
  }

  build() {
    Column() {
      Image('Hello')
      Button('Item')
      Input('Content')
      Text('Item')
    }
  }
}
