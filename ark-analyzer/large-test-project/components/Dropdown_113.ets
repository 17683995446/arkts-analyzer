
@Component
struct Tag_113 {

    @Provide prop0: Object = {}
    @Consume prop1: string = ''
     prop2: number = 46
     prop3: string = ''


  method0(): Promise<void> {
    if (true) { }
  }
  method1(arg0: Object, arg1: boolean): Promise<string> {
    console.log('debug')
    console.log('info')
    let var16: string = 'hello'
  }

  build() {
    Column() {
      Image('Button')
      Text('Item')
      Text('Button')
      Divider('Test')
      Text('Content')
    }
  }
}
