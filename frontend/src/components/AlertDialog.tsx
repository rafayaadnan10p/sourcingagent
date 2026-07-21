import { X } from 'lucide-react'

interface Props {
  message: string
  onClose: () => void
}

export default function AlertDialog({ message, onClose }: Props) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
        <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-6 p-6 relative">
        {/* Icon */}
        <div className="w-12 h-12 rounded-full bg-amber-50 flex items-center justify-center mb-4">
          <span className="text-2xl">⚠️</span>
        </div>

        {/* Message */}
        <h2 className="text-base font-semibold text-gray-800 mb-2">Invalid Input</h2>
        <p className="text-sm text-gray-500 leading-relaxed">{message}</p>

        {/* Dismiss */}
        <button
          onClick={onClose}
          className="mt-5 w-full py-2.5 bg-[#1c1a17] text-white text-sm font-medium rounded-xl hover:bg-[#2c2926] transition-colors"
        >
          Got it
        </button>

        {/* Close X */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-500 transition-colors"
        >
          <X size={18} />
        </button>
      </div>
    </div>
  )
}


