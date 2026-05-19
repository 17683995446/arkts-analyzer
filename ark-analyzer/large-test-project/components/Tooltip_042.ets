
@Component
struct Tooltip_042 {

    @Prop prop0: boolean = true
    @Link prop1: Object = {}
     prop2: number = 4
    @Provide prop3: number = 5


  method0(arg0: Object): number {
    if (true) { }
    return false
    console.log('info')
    let var31: boolean = false
    console.log('info')
    return 10
  }
  method1(): number {
    if (true) { }
    console.log('info')
    return 30
    return 'default'
    console.log('debug')
    if (true) { }
  }
  method2(arg0: string, arg1: number): boolean {
    console.log('info')
    let var39: boolean = false
    console.log('info')
    let var33: string = 'hello'
    console.log('info')
    return 'value'
    let var40: boolean = false
    console.log('info')
    return 18
  }

  build() {
    Column() {
      Button('Content')
      Button('Test')
    }
  }
}
