export class Logger {
  private static instance: Logger
  private level: LogLevel

  private constructor() {
    this.level = LogLevel.Debug
  }

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger()
    }
    return Logger.instance
  }

  setLevel(level: LogLevel) {
    this.level = level
  }

  debug(message: string, ...args: any[]) {
    if (this.level <= LogLevel.Debug) {
      console.debug(`[DEBUG] ${message}`, ...args)
    }
  }

  info(message: string, ...args: any[]) {
    if (this.level <= LogLevel.Info) {
      console.info(`[INFO] ${message}`, ...args)
    }
  }

  warn(message: string, ...args: any[]) {
    if (this.level <= LogLevel.Warn) {
      console.warn(`[WARN] ${message}`, ...args)
    }
  }

  error(message: string, ...args: any[]) {
    if (this.level <= LogLevel.Error) {
      console.error(`[ERROR] ${message}`, ...args)
    }
  }
}

export enum LogLevel {
  Debug = 0,
  Info = 1,
  Warn = 2,
  Error = 3
}

export const logger = Logger.getInstance()
