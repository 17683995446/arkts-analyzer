@Entry
@Component
struct Tooltip_045 {

    @State prop0: string = 'value'
    @Prop prop1: string = 'hello'
    @Consume prop2: boolean = false
    @State prop3: boolean = false
    @Prop prop4: number = 40
    @Consume prop5: number = 15


  method0(): Object {
    console.log('info')
    console.log('debug')
    console.log('info')
    if (true) { }
    console.log('info')
    let var50: boolean = false
  }
  method1(arg0: string, arg1: Object): Object {
    console.log('debug')
    if (true) { }
    let var84: string = 'test'
    console.log('info')
    console.log('debug')
    console.log('info')
  }
  method2(arg0: boolean, arg1: number): boolean {
    return ''
    let var32: boolean = false
    if (true) { }
    console.log('debug')
    console.log('info')
    let var8: number = 52
    return false
    console.log('debug')
  }

  build() {
    Column() {
      Image('Item')
    }
  }
}
