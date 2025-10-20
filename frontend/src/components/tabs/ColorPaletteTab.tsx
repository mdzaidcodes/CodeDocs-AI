'use client';

import { useState } from 'react';
import { Copy, Check, Palette, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Swal from 'sweetalert2';

interface ColorInfo {
  hex: string;
  name: string;
  category: string;
  description: string;
  frequency: number;
  rgb: {
    r: number;
    g: number;
    b: number;
  };
}

interface ColorPalette {
  colors: ColorInfo[];
  total_colors_found: number;
  scheme_type: string;
}

interface ColorPaletteTabProps {
  projectId: string;
  colorPalette: ColorPalette | null;
}

/**
 * Color Palette Tab Component
 * 
 * Displays the extracted color palette from the codebase.
 * Features:
 * - Interactive color swatches
 * - Copy-to-clipboard functionality
 * - Color information (name, hex, RGB, category, usage)
 * - Accessibility contrast score
 * - Color scheme type indicator
 */
export default function ColorPaletteTab({ projectId, colorPalette }: ColorPaletteTabProps) {
  const [copiedColor, setCopiedColor] = useState<string | null>(null);

  /**
   * Calculate contrast ratio between two colors
   * Used for accessibility scoring (WCAG guidelines)
   * 
   * @param rgb1 - First color RGB values
   * @param rgb2 - Second color RGB values  
   * @returns Contrast ratio (1-21)
   */
  const calculateContrastRatio = (
    rgb1: { r: number; g: number; b: number },
    rgb2: { r: number; g: number; b: number }
  ): number => {
    // Calculate relative luminance for each color
    const getLuminance = (rgb: { r: number; g: number; b: number }) => {
      const [r, g, b] = [rgb.r, rgb.g, rgb.b].map((val) => {
        const sRGB = val / 255;
        return sRGB <= 0.03928
          ? sRGB / 12.92
          : Math.pow((sRGB + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    };

    const lum1 = getLuminance(rgb1);
    const lum2 = getLuminance(rgb2);
    
    const lighter = Math.max(lum1, lum2);
    const darker = Math.min(lum1, lum2);
    
    return (lighter + 0.05) / (darker + 0.05);
  };

  /**
   * Get accessibility rating based on contrast ratio
   * 
   * @param ratio - Contrast ratio
   * @returns Object with rating and color
   */
  const getAccessibilityRating = (ratio: number) => {
    if (ratio >= 7) {
      return { rating: 'AAA', color: 'text-green-400', description: 'Excellent' };
    } else if (ratio >= 4.5) {
      return { rating: 'AA', color: 'text-blue-400', description: 'Good' };
    } else if (ratio >= 3) {
      return { rating: 'A', color: 'text-yellow-400', description: 'Fair' };
    } else {
      return { rating: 'Fail', color: 'text-red-400', description: 'Poor' };
    }
  };

  /**
   * Copy color hex code to clipboard
   * Shows success/error toast notification
   * 
   * @param hex - Hex color code to copy
   */
  const copyToClipboard = async (hex: string) => {
    try {
      await navigator.clipboard.writeText(hex);
      setCopiedColor(hex);
      
      // Show success toast
      Swal.fire({
        title: 'Copied!',
        text: `${hex} copied to clipboard`,
        icon: 'success',
        toast: true,
        position: 'bottom-end',
        showConfirmButton: false,
        timer: 2000,
        timerProgressBar: true,
      });

      // Reset copied state after 2 seconds
      setTimeout(() => setCopiedColor(null), 2000);
    } catch (error) {
      Swal.fire({
        title: 'Failed',
        text: 'Could not copy to clipboard',
        icon: 'error',
        toast: true,
        position: 'bottom-end',
        showConfirmButton: false,
        timer: 2000,
      });
    }
  };

  /**
   * Get category badge color
   * 
   * @param category - Color category
   * @returns Tailwind color classes
   */
  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      primary: 'bg-blue-500/20 text-blue-400 border-blue-400/30',
      secondary: 'bg-purple-500/20 text-purple-400 border-purple-400/30',
      accent: 'bg-pink-500/20 text-pink-400 border-pink-400/30',
      background: 'bg-gray-500/20 text-gray-400 border-gray-400/30',
      text: 'bg-slate-500/20 text-slate-400 border-slate-400/30',
      success: 'bg-green-500/20 text-green-400 border-green-400/30',
      error: 'bg-red-500/20 text-red-400 border-red-400/30',
      warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-400/30',
      info: 'bg-cyan-500/20 text-cyan-400 border-cyan-400/30',
      border: 'bg-indigo-500/20 text-indigo-400 border-indigo-400/30',
    };
    return colors[category.toLowerCase()] || 'bg-white/10 text-white border-white/20';
  };

  /**
   * Get scheme type badge color
   * 
   * @param schemeType - Color scheme type ('dark', 'light', 'mixed')
   * @returns Tailwind color classes
   */
  const getSchemeTypeColor = (schemeType: string) => {
    const colors: Record<string, string> = {
      dark: 'bg-gray-900 text-white border-gray-700',
      light: 'bg-gray-100 text-gray-900 border-gray-300',
      mixed: 'bg-gradient-to-r from-gray-900 to-gray-100 text-white border-white/20',
    };
    return colors[schemeType] || 'bg-white/10 text-white border-white/20';
  };

  // Handle empty or null palette
  if (!colorPalette || !colorPalette.colors || colorPalette.colors.length === 0) {
    return (
      <div className="text-center py-16 bg-white/5 rounded-lg border border-white/10">
        <Palette className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-white mb-2">
          No Color Palette Available
        </h3>
        <p className="text-gray-400">
          Color extraction is still in progress or no colors were found in the codebase.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Scheme Type */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center">
            <Palette className="h-6 w-6 mr-2 text-blue-400" />
            Design System & Color Palette
          </h2>
          <p className="text-gray-400 mt-1">
            Top {colorPalette.colors.length} colors extracted from {colorPalette.total_colors_found} unique colors
          </p>
        </div>
        
        {/* Color Scheme Type Badge */}
        <div className={`px-4 py-2 rounded-lg border-2 ${getSchemeTypeColor(colorPalette.scheme_type)}`}>
          <span className="font-semibold capitalize">{colorPalette.scheme_type} Theme</span>
        </div>
      </div>

      {/* Color Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
        {colorPalette.colors.map((color, index) => {
          // Calculate contrast against white and black backgrounds
          const contrastWhite = calculateContrastRatio(color.rgb, { r: 255, g: 255, b: 255 });
          const contrastBlack = calculateContrastRatio(color.rgb, { r: 0, g: 0, b: 0 });
          const bestContrast = Math.max(contrastWhite, contrastBlack);
          const accessibilityRating = getAccessibilityRating(bestContrast);
          
          return (
            <div
              key={index}
              className="bg-white/5 rounded-lg border border-white/10 overflow-hidden hover:border-blue-400/50 transition-all hover:scale-105 hover:shadow-lg hover:shadow-blue-500/20"
            >
              {/* Color Swatch - Clickable to copy */}
              <button
                onClick={() => copyToClipboard(color.hex)}
                className="w-full h-32 relative group cursor-pointer transition-all"
                style={{ backgroundColor: color.hex }}
              >
                {/* Copy indicator overlay */}
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  {copiedColor === color.hex ? (
                    <Check className="h-8 w-8 text-green-400" />
                  ) : (
                    <Copy className="h-8 w-8 text-white" />
                  )}
                </div>
                
                {/* Frequency indicator */}
                <div className="absolute top-2 right-2 bg-black/70 px-2 py-1 rounded text-xs text-white">
                  Used {color.frequency}x
                </div>
              </button>

              {/* Color Information */}
              <div className="p-4 space-y-3">
                {/* Color Name */}
                <div>
                  <h3 className="text-lg font-semibold text-white mb-1">{color.name}</h3>
                  <span className={`inline-block px-2 py-1 rounded text-xs border ${getCategoryColor(color.category)}`}>
                    {color.category}
                  </span>
                </div>

                {/* Hex and RGB Values */}
                <div className="space-y-1 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">HEX:</span>
                    <code className="text-blue-300 font-mono">{color.hex}</code>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">RGB:</span>
                    <code className="text-blue-300 font-mono text-xs">
                      {color.rgb.r}, {color.rgb.g}, {color.rgb.b}
                    </code>
                  </div>
                </div>

                {/* Accessibility Score */}
                <div className="pt-2 border-t border-white/10">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-gray-400 text-xs flex items-center">
                      <Info className="h-3 w-3 mr-1" />
                      Contrast
                    </span>
                    <span className={`text-xs font-semibold ${accessibilityRating.color}`}>
                      {accessibilityRating.rating}
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        accessibilityRating.rating === 'AAA'
                          ? 'bg-green-500'
                          : accessibilityRating.rating === 'AA'
                          ? 'bg-blue-500'
                          : accessibilityRating.rating === 'A'
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${Math.min((bestContrast / 7) * 100, 100)}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Ratio: {bestContrast.toFixed(2)}:1
                  </p>
                </div>

                {/* Usage Description */}
                <div className="pt-2 border-t border-white/10">
                  <p className="text-xs text-gray-300 leading-relaxed">
                    {color.description}
                  </p>
                </div>

                {/* Copy Button */}
                <Button
                  onClick={() => copyToClipboard(color.hex)}
                  variant="outline"
                  size="sm"
                  className="w-full border-white/20 text-white hover:bg-white/10"
                >
                  {copiedColor === color.hex ? (
                    <>
                      <Check className="h-3 w-3 mr-2" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="h-3 w-3 mr-2" />
                      Copy {color.hex}
                    </>
                  )}
                </Button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Accessibility Legend */}
      <div className="bg-white/5 rounded-lg border border-white/10 p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <Info className="h-5 w-5 mr-2 text-blue-400" />
          Accessibility Guidelines (WCAG)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-gray-300">
              <strong className="text-green-400">AAA</strong> - 7:1+ ratio (Excellent)
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span className="text-gray-300">
              <strong className="text-blue-400">AA</strong> - 4.5:1+ ratio (Good)
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span className="text-gray-300">
              <strong className="text-yellow-400">A</strong> - 3:1+ ratio (Fair)
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span className="text-gray-300">
              <strong className="text-red-400">Fail</strong> - Below 3:1 (Poor)
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

