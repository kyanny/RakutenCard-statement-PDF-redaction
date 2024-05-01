#!/usr/bin/env ruby
# require 'pdf/reader'
require 'hexapdf'

filename = "statement_202402.pdf"

# PDF::Reader.open(filename) do |reader|
#   reader.pages.each do |page|
#     #puts page.text.encoding
#     # page.walk(PDF::Reader::PageTextReceiver.new) do |receiver|
#     #   puts receiver.text
#     # end
#     pp page.raw_content
#   end
# end

# require 'hexapdf'

# doc = HexaPDF::Document.open(filename)
# pp doc
# pp doc.pages.size
# page = doc.pages.first

# pp page

# # iterate page contents
# page.contents.each do |content|
#   pp content
# end


require 'hexapdf'

class ShowTextProcessor < HexaPDF::Content::Processor

  def initialize(page)
    super()
    @canvas = page.canvas(type: :overlay)
  end

  def show_text(str)
    boxes = decode_text_with_positioning(str)
    return if boxes.string.empty?

    @canvas.line_width = 1
    @canvas.stroke_color(224, 0, 0)
    # Polyline for transformed characters
    #boxes.each {|box| @canvas.polyline(*box.points).close_subpath.stroke}
    # Using rectangles is faster but not 100% correct
    boxes.each do |box|
      x, y = *box.lower_left
      tx, ty = *box.upper_right
      @canvas.rectangle(x, y, tx - x, ty - y).stroke
    end

    @canvas.line_width = 0.5
    @canvas.stroke_color(0, 224, 0)
    @canvas.polyline(*boxes.lower_left, *boxes.lower_right,
                     *boxes.upper_right, *boxes.upper_left).close_subpath.stroke
  end
  alias :show_text_with_positioning :show_text

end

#doc = HexaPDF::Document.open(ARGV.shift)
doc = HexaPDF::Document.open(filename)
doc.config['font.on_missing_unicode_mapping'] = proc { |code, font_dict|
  # warn code
  "x"
}
doc.pages.each_with_index do |page, index|
  puts "Processing page #{index + 1}"
  processor = ShowTextProcessor.new(page)
  page.process_contents(processor)
end
doc.write('show_char_boxes.pdf', optimize: true)
