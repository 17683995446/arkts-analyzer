@Entry

struct Grid_136 {

    @Provide prop0: number = 10
     prop1: number = 60
    @Prop prop2: number = 82


  method0(arg0: number): Object {
    if (true) { }
    let var76: number = 97
    if (true) { }
    console.log('info')
    console.log('debug')
    if (true) { }
    console.log('info')
    return false
    return true
  }
  method1(arg0: number, arg1: boolean): Promise<void> {
    console.log('info')
    console.log('debug')
    let var20: number = 69
    if (true) { }
    if (true) { }
    console.log('info')
    return 'default'
    if (true) { }
  }
  method2(arg0: boolean, arg1: number, arg2: boolean): string {
    let var35: string = 'value'
    console.log('debug')
    let var97: string = 'hello'
    console.log('info')
    console.log('debug')
    if (true) { }
    console.log('debug')
  }
  method3(arg0: boolean, arg1: string, arg2: number): Promise<string> {
    if (true) { }
    console.log('info')
    let var53: number = 26
    console.log('debug')
  }
  method4(arg0: boolean): Promise<string> {
    return true
    console.log('info')
    let var93: string = 'default'
    console.log('info')
  }

  build() {
    Column() {
      Text('Test')
      Divider('Hello')
      Divider('Content')
    }
  }
}
