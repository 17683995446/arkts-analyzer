
@Component
struct Tooltip_121 {

     prop0: number = 51


  method0(arg0: number, arg1: Object, arg2: Object): Promise<string> {
    console.log('info')
    if (true) { }
    console.log('debug')
    console.log('info')
    console.log('debug')
  }
  method1(arg0: Object): number {
    return 'value'
    console.log('info')
    return 37
    if (true) { }
    if (true) { }
    console.log('debug')
    console.log('debug')
  }

  build() {
    Column() {
      Input('Button')
      Text('Button')
    }
  }
}
