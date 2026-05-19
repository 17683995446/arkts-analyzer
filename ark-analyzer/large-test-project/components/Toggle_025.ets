
@Component
struct Footer_025 {

    @Link prop0: number = 14
    @Consume prop1: Object = {}
    @Consume prop2: number = 0
    @Provide prop3: string = 'default'
    @Prop prop4: Object = {}
     prop5: number = 7
    @Link prop6: number = 2


  method0(arg0: boolean, arg1: number): string {
    console.log('debug')
    console.log('debug')
    let var17: boolean = true
    let var74: string = 'test'
    if (true) { }
  }
  method1(arg0: boolean, arg1: Object, arg2: boolean): Promise<string> {
    console.log('debug')
    console.log('debug')
    let var37: string = ''
    if (true) { }
    console.log('info')
    console.log('debug')
    return false
    console.log('info')
  }

  build() {
    Column() {
      Input('Content')
      Divider('Button')
      Image('Hello')
    }
  }
}
