
@Component
struct Tabs_087 {

    @State prop0: string = ''
    @Prop prop1: Object = {}
    @Link prop2: string = 'test'
    @Consume prop3: boolean = false
    @Provide prop4: number = 95
    @Consume prop5: boolean = true


  method0(arg0: Object, arg1: string, arg2: string): Promise<string> {
    console.log('info')
    if (true) { }
    return 34
    console.log('debug')
    console.log('info')
    if (true) { }
    return 'default'
  }
  method1(arg0: string, arg1: number): Object {
    if (true) { }
    console.log('info')
    if (true) { }
    let var3: string = 'hello'
    return ''
  }
  method2(arg0: string, arg1: boolean): boolean {
    console.log('info')
    let var21: boolean = false
    console.log('info')
    let var1: string = ''
    if (true) { }
    if (true) { }
    let var63: boolean = false
    console.log('debug')
    console.log('info')
  }
  method3(arg0: boolean, arg1: number, arg2: number): Object {
    return 35
    console.log('info')
    return 13
    let var79: string = 'hello'
    console.log('info')
  }
  method4(): Promise<void> {
    if (true) { }
    if (true) { }
    console.log('debug')
    if (true) { }
    return false
    return true
    return 'hello'
    return 88
    return 'value'
  }

  build() {
    Column() {
      Divider('Item')
      Text('Hello')
      Input('Item')
      Divider('Test')
      Text('Item')
    }
  }
}
