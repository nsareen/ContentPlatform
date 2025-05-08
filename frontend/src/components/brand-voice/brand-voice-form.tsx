import { useState } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { BrandVoice } from "./brand-voice-card";

// Define the form schema with Zod
const brandVoiceSchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().min(1, "Description is required"),
  dos: z.string().optional(),
  donts: z.string().optional(),
  voice_metadata: z.object({
    personality: z.string().optional(),
    tonality: z.string().optional(),
  }).optional(),
});

type BrandVoiceFormData = z.infer<typeof brandVoiceSchema>;

interface BrandVoiceFormProps {
  initialData?: Partial<BrandVoice>;
  onSubmit: (data: BrandVoiceFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function BrandVoiceForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}: BrandVoiceFormProps) {
  const [activeTab, setActiveTab] = useState<"details" | "guidelines">("details");
  
  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<BrandVoiceFormData>({
    resolver: zodResolver(brandVoiceSchema),
    defaultValues: {
      name: initialData?.name || "",
      description: initialData?.description || "",
      dos: initialData?.dos || "",
      donts: initialData?.donts || "",
      voice_metadata: {
        personality: initialData?.voice_metadata?.personality || "",
        tonality: initialData?.voice_metadata?.tonality || "",
      },
    },
  });

  const onFormSubmit = (data: BrandVoiceFormData) => {
    onSubmit(data);
  };

  return (
    <div className="card">
      <div className="border-b border-border-default">
        <div className="flex">
          <button
            className={`px-4 py-3 text-sm font-medium ${
              activeTab === "details"
                ? "text-primary border-b-2 border-primary"
                : "text-text-secondary hover:text-text-primary"
            }`}
            onClick={() => setActiveTab("details")}
          >
            Basic Details
          </button>
          <button
            className={`px-4 py-3 text-sm font-medium ${
              activeTab === "guidelines"
                ? "text-primary border-b-2 border-primary"
                : "text-text-secondary hover:text-text-primary"
            }`}
            onClick={() => setActiveTab("guidelines")}
          >
            Guidelines
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit(onFormSubmit)} className="p-6">
        {activeTab === "details" && (
          <div className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-text-primary mb-1">
                Brand Voice Name
              </label>
              <input
                id="name"
                type="text"
                className={`input ${
                  errors.name ? "border-feedback-error" : ""
                }`}
                placeholder="e.g., Laureate Asia-Pacific"
                {...register("name")}
              />
              {errors.name && (
                <p className="mt-1 text-xs text-feedback-error">{errors.name.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-text-primary mb-1">
                Description
              </label>
              <textarea
                id="description"
                rows={3}
                className={`input ${
                  errors.description ? "border-feedback-error" : ""
                }`}
                placeholder="e.g., Bold, expressive, and effortlessly stylish"
                {...register("description")}
              />
              {errors.description && (
                <p className="mt-1 text-xs text-feedback-error">{errors.description.message}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="personality" className="block text-sm font-medium text-text-primary mb-1">
                  Personality
                </label>
                <Controller
                  name="voice_metadata.personality"
                  control={control}
                  render={({ field }) => (
                    <input
                      id="personality"
                      type="text"
                      className="input"
                      placeholder="e.g., Bold, confident, sophisticated"
                      {...field}
                    />
                  )}
                />
              </div>
              <div>
                <label htmlFor="tonality" className="block text-sm font-medium text-text-primary mb-1">
                  Tonality
                </label>
                <Controller
                  name="voice_metadata.tonality"
                  control={control}
                  render={({ field }) => (
                    <input
                      id="tonality"
                      type="text"
                      className="input"
                      placeholder="e.g., Energetic, friendly, authoritative"
                      {...field}
                    />
                  )}
                />
              </div>
            </div>
          </div>
        )}

        {activeTab === "guidelines" && (
          <div className="space-y-6">
            <div>
              <label htmlFor="dos" className="block text-sm font-medium text-text-primary mb-1">
                Do's
              </label>
              <textarea
                id="dos"
                rows={5}
                className="input"
                placeholder="e.g., Maintain an empowering and confident tone"
                {...register("dos")}
              />
            </div>

            <div>
              <label htmlFor="donts" className="block text-sm font-medium text-text-primary mb-1">
                Don'ts
              </label>
              <textarea
                id="donts"
                rows={5}
                className="input"
                placeholder="e.g., Don't overload with technical details"
                {...register("donts")}
              />
            </div>
          </div>
        )}

        <div className="mt-8 flex justify-end gap-3">
          <button
            type="button"
            className="btn-secondary"
            onClick={onCancel}
            disabled={isLoading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn-primary disabled:opacity-70 disabled:cursor-not-allowed"
            disabled={isLoading}
          >
            {isLoading ? (
              <span className="flex items-center">
                <svg
                  className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Saving...
              </span>
            ) : (
              "Save Brand Voice"
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
