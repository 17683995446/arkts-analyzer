
@Component
struct List_008 {

     prop0: boolean = false
     prop1: number = 39
    @Consume prop2: boolean = true


  method0(arg0: Object): number {
    console.log('debug')
  }
  method1(arg0: string, arg1: Object, arg2: number): Promise<string> {
    console.log('info')
    if (true) { }
    console.log('debug')
    if (true) { }
    console.log('debug')
    return true
  }

  build() {
    Column() {
      Divider('Content')
      Button('Item')
    }
  }
}
