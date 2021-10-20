require_relative 'filter'

class Parser

  attr_reader :parsed_data

  def self.run(data)
    parser = Parser.new(data)
    parser.parse
    parser
  end

  def initialize(data)
    @data = data
  end

  def parse
    @parsed_data = @data.to_s.split(';').map{|x| x.split('|')}.map{|x| x.map{|x| x.split(',').map(&:to_f)}}

    unless @parsed_data.map {|x| x.map(&:length).uniq}.uniq == [[3]]
      raise 'Bad Input. Ensure data is properly formatted.'
    end

    if @parsed_data.first.count == 1
      filtered_accl = @parsed_data.map(&:flatten).transpose.map do |total_accl|
        grav = Filter.low_0_hz(total_accl)
        user = total_accl.zip(grav).map{|a, b| a - b}
        [user, grav]
      end

      @parsed_data = @parsed_data.length.times.map do |i|
        user = filtered_accl.map(&:first).map{|elem| elem[i]}
        grav = filtered_accl.map(&:last).map{|elem| elem[i]}
        [user, grav]
      end
    end
  end

end
