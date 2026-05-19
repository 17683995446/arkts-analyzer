@Component
struct ButtonComponent {
  @Prop label: string
  @Prop type: ButtonType = ButtonType.Normal
  @Prop disabled: boolean = false
  @Link clickHandler: () => void

  build() {
    Button(this.label)
      .type(this.type)
      .enabled(!this.disabled)
      .onClick(() => {
        if (!this.disabled && this.clickHandler) {
          this.clickHandler()
        }
      })
      .backgroundColor(this.getBackgroundColor())
      .fontColor(this.getFontColor())
      .borderRadius(8)
      .width('100%')
      .height(44)
  }

  private getBackgroundColor(): string {
    if (this.disabled) {
      return '#cccccc'
    }
    switch (this.type) {
      case ButtonType.Primary:
        return '#00d4ff'
      case ButtonType.Danger:
        return '#ff4d4f'
      case ButtonType.Success:
        return '#52c41a'
      default:
        return '#ffffff'
    }
  }

  private getFontColor(): string {
    if (this.type === ButtonType.Primary || this.type === ButtonType.Success) {
      return '#000000'
    }
    return '#ffffff'
  }
}

export enum ButtonType {
  Normal,
  Primary,
  Danger,
  Success
}

export default ButtonComponent
