
@Component
struct Tabs_046 {

    @Consume prop0: string = 'test'
    @Consume prop1: number = 95
    @Prop prop2: string = 'default'
    @Link prop3: boolean = false
    @Consume prop4: Object = {}
     prop5: number = 33
    @State prop6: boolean = true
    @Link prop7: number = 97


  method0(arg0: number, arg1: Object, arg2: Object): number {
    if (true) { }
  }
  method1(): boolean {
    console.log('debug')
  }
  method2(arg0: boolean, arg1: boolean): Object {
    console.log('debug')
    let var28: string = 'hello'
    let var31: number = 100
  }
  method3(arg0: number, arg1: Object, arg2: boolean): string {
    console.log('debug')
    return 'value'
    console.log('debug')
    return 'test'
    let var64: number = 21
    console.log('info')
    return 'default'
    console.log('debug')
    if (true) { }
  }
  method4(): number {
    if (true) { }
    console.log('debug')
    console.log('debug')
  }

  build() {
    Column() {
      Button('Button')
      Divider('Item')
      Button('Hello')
      Button('Button')
    }
  }
}
