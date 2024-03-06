export default function Branding() {
  return (
    <div className="absolute bottom-3 right-3 text-xs flex items-center">
      Powered by{' '}
      <img
        src="https://storage.googleapis.com/fini-widget-dev/assets/fini.png"
        alt="fini-logo"
        className="mx-1 w-3"
      />
      <a href="https://usefini.com" target="_blank" className="text-[#2084FF]">
        <b>Fini</b>
      </a>
    </div>
  )
}
