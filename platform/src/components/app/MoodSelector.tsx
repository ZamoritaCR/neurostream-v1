"use client";

interface MoodSelectorProps {
  selectedMood: string;
  onMoodChange: (mood: string) => void;
  label: string;
}

const moods = [
  { value: "anxious", label: "Anxious", color: "border-yellow-500" },
  { value: "happy", label: "Happy", color: "border-green-500" },
  { value: "sad", label: "Sad", color: "border-blue-500" },
  { value: "bored", label: "Bored", color: "border-gray-500" },
  { value: "energized", label: "Energized", color: "border-red-500" },
  { value: "tired", label: "Tired", color: "border-purple-500" },
  { value: "stressed", label: "Stressed", color: "border-orange-500" },
  { value: "calm", label: "Calm", color: "border-cyan-500" },
];

export function MoodSelector({
  selectedMood,
  onMoodChange,
  label,
}: MoodSelectorProps) {
  return (
    <div>
      <label className="block text-sm font-medium mb-3">{label}</label>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {moods.map((mood) => (
          <button
            key={mood.value}
            onClick={() => onMoodChange(mood.value)}
            className={`p-4 rounded-lg border-2 transition-all ${
              selectedMood === mood.value
                ? `${mood.color} bg-surface-hover`
                : "border-border hover:border-muted"
            }`}
          >
            <span className="text-lg">{mood.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
