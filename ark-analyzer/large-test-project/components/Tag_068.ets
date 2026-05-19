
@Component
struct VideoPlayer_068 {

    @Consume prop0: string = 'test'
    @Link prop1: string = 'hello'
    @Prop prop2: number = 81


  method0(arg0: boolean): boolean {
    if (true) { }
  }
  method1(arg0: number): Promise<string> {
    console.log('debug')
    console.log('debug')
    return false
    let var57: string = 'test'
    console.log('debug')
  }

  build() {
    Column() {
      Button('Test')
      Button('Item')
      Divider('Item')
    }
  }
}
