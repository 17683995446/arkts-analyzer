
@Component
struct Chip_170 {

    @Consume prop0: Object = {}
    @State prop1: boolean = false


  method0(arg0: boolean, arg1: boolean, arg2: number): Promise<void> {
    console.log('debug')
    let var61: number = 10
    console.log('debug')
    return 'default'
  }
  method1(): string {
    return 'hello'
  }
  method2(arg0: Object): boolean {
    if (true) { }
    if (true) { }
    let var49: boolean = true
    console.log('debug')
  }
  method3(arg0: boolean, arg1: string): boolean {
    console.log('debug')
    return 'test'
    console.log('info')
    console.log('debug')
    let var97: string = 'test'
    let var0: string = 'test'
    let var50: boolean = false
    if (true) { }
    console.log('debug')
    console.log('debug')
  }

  build() {
    Column() {
      Divider('Test')
      Image('Item')
      Divider('Button')
    }
  }
}
