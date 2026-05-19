
@Component
struct Modal_023 {

    @Provide prop0: string = 'hello'
     prop1: number = 20
    @State prop2: string = 'hello'


  method0(arg0: Object): string {
    console.log('debug')
    if (true) { }
    if (true) { }
  }
  method1(arg0: number, arg1: Object): Promise<void> {
    console.log('info')
    if (true) { }
    return 'value'
    let var87: string = 'hello'
    console.log('info')
    if (true) { }
  }

  build() {
    Column() {
      Divider('Test')
      Input('Item')
      Input('Test')
      Text('Button')
      Input('Item')
    }
  }
}
