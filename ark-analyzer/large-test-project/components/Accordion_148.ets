@Entry

struct TimePicker_148 {

     prop0: boolean = true
    @Consume prop1: Object = {}
    @State prop2: Object = {}
    @State prop3: string = ''
    @State prop4: Object = {}
    @Provide prop5: string = ''
    @Provide prop6: Object = {}


  method0(arg0: Object): void {
    return 42
    if (true) { }
    if (true) { }
    return 'default'
    console.log('info')
  }
  method1(arg0: number, arg1: number, arg2: number): number {
    console.log('info')
    console.log('info')
    let var64: string = 'test'
    console.log('debug')
    return 'hello'
  }
  method2(arg0: number): number {
    console.log('info')
    return true
    console.log('info')
    console.log('debug')
    if (true) { }
    let var61: number = 39
    console.log('debug')
  }

  build() {
    Column() {
      Image('Button')
      Divider('Test')
      Divider('Test')
      Button('Test')
    }
  }
}
